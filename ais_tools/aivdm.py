"""
Tools for decoding AIS messages in AIVDM format
"""

import json
import re
from datetime import datetime
from collections import defaultdict

import ais as libais
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from ais import stream as libais_stream


TAGBLOCK_T_FORMAT = '%Y-%m-%d %H.%M.%S'


def safe_tagblock_timestamp(line):
    """
    attempt to extract the tagblock timestamp without triggering any exceptions
    This is used for reporting messages that fail to decode
    returns 0 if no timestamp can be found
    """

    try:
        if line.startswith("\\"):
            tagblock = line[1:].split("\\", 1)[0]
            tagblock = tagblock.split("*")[0]
            for field in tagblock.split(","):
                parts = field.split(":")
                if len(parts) == 2:
                    key, value = parts
                    if key == 'c':
                        t = int(value)
                        return t if t <= 40000000000 else t/1000
    except ValueError:
        pass

    return 0


def tagblock_t(dt):
    return dt.strftime(TAGBLOCK_T_FORMAT)


def compute_checksum(sentence):
    """Compute the NMEA checksum for a payload."""
    c = 0
    for char in sentence:
        c ^= ord(char)
    checksum_str = '%02x' % c
    return checksum_str.upper()


def tagblock(station, timestamp=None, add_tagblock_t=True):
    dt = timestamp or datetime.utcnow()
    params = dict(
        c=round(dt.timestamp()*1000),
        s=station,
        T=tagblock_t(dt)
    )
    param_str = ','.join(["{}:{}".format(k, v) for k, v in params.items()])
    checksum = compute_checksum(param_str)
    return '{}*{}'.format(param_str, checksum)


def validate_field_types(msg):
    """
    validate data types for some fields which are returned by libais with incorrect types
    under some error conditions

    This is needed to address a bug in libais mentioned here: https://github.com/schwehr/libais/issues/179
    """
    try:
        int(msg.get('spare2', 0))
    except TypeError as e:
        raise libais.DecodeError('Type check failed in field %s (%s)' % ('spare2', str(e)))


def _decode(body, pad):
    res = libais.decode(body, pad)
    validate_field_types(res)
    return res


def decode_nmea_body(body, pad):
    try:
        return _decode(body, pad)
    except libais.DecodeError as e:
        # Special case for issue #1 - some type 24 messages have incorrect length

        if str(e) == 'Ais24: AIS_ERR_BAD_BIT_COUNT' and len(body) == 27:
            body = body + '0'
        else:
            raise

    # Try the decode again
    return _decode(body, pad)


def expand_nmea(line):
    try:
        tagblock, nmea = libais_stream.parseTagBlock(line)
    except ValueError as e:
        raise libais.DecodeError('Failed to parse tagblock (%s) %s' % (str(e), line))

    nmea = nmea.strip()
    fields = nmea.split(',')
    if len(fields) < 6:
        raise libais.DecodeError('not enough fields in nmea message')

    if not libais_stream.checksum.isChecksumValid(nmea):
        raise libais.DecodeError('Invalid checksum')

    try:
        tagblock['tagblock_groupsize'] = int(fields[1])
        tagblock['tagblock_sentence'] = int(fields[2])
        if fields[3] != '':
            tagblock['tagblock_id'] = int(fields[3])
        tagblock['tagblock_channel'] = fields[4]
        body = fields[5]
        pad = int(nmea.split('*')[0][-1])
    except ValueError:
        raise libais.DecodeError('Unable to convert field to int in nmea message')

    if 'tagblock_group' in tagblock:
        tagblock_group = tagblock.get('tagblock_group', {})
        del tagblock['tagblock_group']
        group_fields = {'tagblock_' + k: v for k, v in tagblock_group.items()}
        tagblock.update(group_fields)

    return tagblock, body, pad


def safe_decode_message(line):
    msg = {}
    try:
        msg = decode_message(line)
    except libais.DecodeError as e:
        msg = dict(
            nmea=line,
            error=str(e)
        )
    return msg


def decode_message(line):

    msg = dict(nmea=line)

    parts = [expand_nmea(line) for line in split_multipart(line)]

    if len(parts) == 1:
        # single part message
        tagblock, body, pad = parts[0]
    else:
        # multipart message
        parts = sorted(parts, key=lambda x: x[1]['part_num'])
        tagblocks, bodys, pads = list(zip(*parts))

        # merge the tagblocks, prefer the values in the first message
        tagblock = {}
        for t in reversed(tagblocks):
            tagblock.update(t)

        # concatenate the nmea body elements
        body = ''.join([body for body in bodys])

        # pad value comes from the final part
        pad = pads[-1]

    msg.update(tagblock)
    msg.update(decode_nmea_body(body, pad))
    validate_field_types(msg)

    return msg


def decode_stream(lines):
    for line in lines:
        yield decode_message(line)


def split_multipart(line):
    """
    Split a single line of text that contains one or more nmea messages
    Expects the combined lines to have been joined with join_multipart()

    Each message part is expected to be one of these
        !AIDVM....
        \\!AIDVM....
        \\tagblock\\!AIDVM....

    and all parts in the line should have the same format
    """
    if line.startswith('!'):
        regex = r'(![^!]+)'
    elif line.startswith('\\!'):
        regex = r'(\\![^!\\]+)'
    elif line.startswith('\\'):
        regex = r'(\\[^\\]+\\![^!\\]+)'
    else:
        raise ValueError

    return re.findall(regex, line)


def join_multipart(lines):
    """
    takes a list of nmea text lines that form a single mulitpart message and concatenates them in the order given
    """
    start_chars = {line[0] for line in lines}
    if len(start_chars) == 1 and start_chars.issubset({'\\', '!'}):
        return ''.join(lines)
    raise ValueError("all lines to be joined must start with the same character, either '\\' or '!'")


def join_multipart_stream(lines, max_time_window=2, max_message_window=1000, ignore_decode_errors=False):
    """
    Takes a stream of nmea text lines and tries to find the matching parts of multi part messages
    which may not be adjacent in the stream and may come out of order.

    Matched message parts will be concatenated together into a single line using join_multipart()
    All other messages will come out with no changes
    """
    buffer = defaultdict(list)

    for index, line in enumerate(lines):
        try:
            tagblock, body, pad = expand_nmea(line)
        except libais.DecodeError:
            if ignore_decode_errors:
                yield line
                continue
            else:
                raise

        now = datetime.utcnow().timestamp()
        if tagblock['tagblock_groupsize'] == 1:
            # this is a single part part message, so nothing to do, just pass it out
            yield line
        else:
            # part_num = int(fields[2])
            key = (tagblock.get('tagblock_groupsize'), tagblock.get('tagblock_station'),
                   tagblock.get('tagblock_id'), tagblock.get('tagblock_channel'))
            part = dict(part_num=tagblock['tagblock_sentence'], line=line, index=index, time_in=now)

            buffered_part_nums = set(part['part_num'] for part in buffer[key])
            if part['part_num'] in buffered_part_nums:
                # already another message part with this part_num in the buffer, so flush out the unmatched parts
                for part in sorted(buffer[key], key=lambda x: x['index']):
                    yield part['line']
                # replace the slot in the buffer with the new part
                buffer[key] = [part]

            elif buffered_part_nums.union({tagblock['tagblock_sentence']}) == set(range(1, tagblock['tagblock_groupsize'] + 1)):
                # found all the parts.   Concatenate them in order and send the combined line out
                buffer[key].append(part)
                yield ''.join([part['line'] for part in sorted(buffer[key], key=lambda x:x['part_num'])])
                del buffer[key]

            else:
                buffer[key].append(part)

        # flush old parts from the buffer
        flush_keys = set()
        flush_time = now - max_time_window
        flush_index = index - max_message_window

        # find any keys that have at least one part that is too old
        for key, parts in buffer.items():
            if any(part['time_in'] < flush_time or part['index'] < flush_index for part in parts):
                flush_keys.add(key)

        # flush out all the unmatched parts for all keys that have at least one old part.
        # Send them out in the order they arrived
        flush_parts = []
        for key in flush_keys:
            flush_parts += buffer[key]
            del buffer[key]
        for part in sorted(flush_parts, key=lambda x: x['index']):
            yield part['line']

    # input stream ended, so flush whatever parts are left in the buffer in the order they arrived
    for key, parts in buffer.items():
        for part in sorted(parts, key=lambda x: x['index']):
            yield part['line']

