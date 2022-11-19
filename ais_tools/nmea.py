from collections import defaultdict
from datetime import datetime
import re

from ais import DecodeError
from ais_tools.checksum import is_checksum_valid
from ais_tools.tagblock import parseTagBlock

REGEX_BANG = re.compile(r'(![^!]+)')
REGEX_BACKSLASH = re.compile(r'(\\[^\\]+\\![^!\\]+)')
REGEX_BACKSLASH_BANG = re.compile(r'(\\![^!\\]+)')


def expand_nmea(line, validate_checksum=False):
    try:
        tagblock, nmea = parseTagBlock(line)
    except ValueError as e:
        raise DecodeError('Failed to parse tagblock (%s) %s' % (str(e), line))

    nmea = nmea.strip()
    fields = nmea.split(',')
    if len(fields) < 6:
        raise DecodeError('not enough fields in nmea message')

    if validate_checksum and not is_checksum_valid(nmea):
        raise DecodeError('Invalid checksum')

    try:
        tagblock['tagblock_groupsize'] = int(fields[1])
        tagblock['tagblock_sentence'] = int(fields[2])
        if fields[3] != '':
            tagblock['tagblock_id'] = int(fields[3])
        tagblock['tagblock_channel'] = fields[4]
        body = fields[5]
        pad = int(nmea.split('*')[0][-1])
    except ValueError:
        raise DecodeError('Unable to convert field to int in nmea message')

    if 'tagblock_group' in tagblock:
        tagblock_group = tagblock.get('tagblock_group', {})
        del tagblock['tagblock_group']
        group_fields = {'tagblock_' + k: v for k, v in tagblock_group.items()}
        tagblock.update(group_fields)

    return tagblock, body, pad


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
        regex = REGEX_BANG
    elif line.startswith('\\!'):
        regex = REGEX_BACKSLASH_BANG
    elif line.startswith('\\'):
        regex = REGEX_BACKSLASH
    else:
        raise DecodeError('no valid AIVDM message detected')

    return regex.findall(line)


def join_multipart(lines):
    """
    takes a list of nmea text lines that form a single mulitpart message and concatenates them in the order given
    """
    start_chars = {line[0] for line in lines}
    if len(start_chars) == 1 and start_chars.issubset({'\\', '!'}):
        return ''.join(lines)
    raise DecodeError("all lines to be joined must start with the same character, either '\\' or '!'")


def safe_join_multipart_stream(lines, max_time_window=500, max_message_window=1000, use_station_id=True):
    """
    Same as join_multipart_stream but for any message that cannot decoded, it will just emit
    that message back out and not raise a DecodeError exception
    """
    lines = join_multipart_stream(
            lines,
            max_time_window=max_time_window,
            max_message_window=max_message_window,
            ignore_decode_errors=True,
            use_station_id=use_station_id
            )
    for line in lines:
        yield line


def join_multipart_stream(lines,
                          max_time_window=500,
                          max_message_window=1000,
                          ignore_decode_errors=False,
                          use_station_id=True):
    """
    Takes a stream of nmea text lines and tries to find the matching parts of multi part messages
    which may not be adjacent in the stream and may come out of order.

    Matched message parts will be concatenated together into a single line using join_multipart()
    All other messages will come out with no changes
    """
    buffer = defaultdict(list)

    for index, line in enumerate(lines):
        line = line.strip()
        try:
            tagblock, body, pad = expand_nmea(line)
        except DecodeError:
            if ignore_decode_errors:
                yield line
                continue
            else:
                raise

        now = datetime.utcnow().timestamp()
        total_parts = tagblock['tagblock_groupsize']

        if total_parts == 1:
            # this is a single part part message, so nothing to do, just pass it out
            yield line
        else:
            # make a key for matching message parts
            # - tagblock_groupsize is the number of parts we are looking for
            # - tagblock_station is the source of the message and may not have a value
            # - tagblock_id is a sequence number that is the same for all message parts, but it is not unique
            # - tagblock_channel is the AIS RF channel (either A or B) that was used for transmission

            station_id = tagblock.get('tagblock_station') if use_station_id else None
            key = (total_parts, station_id, tagblock.get('tagblock_id'),
                   tagblock.get('tagblock_channel'))

            # pack up the message part
            # - tagblock_sentence is the index of this part relative to the other parts, where the first part is 1
            # - line is the nmea that was passed in
            # - index is the index of this line in the stream - needed to flush old messages
            # - time_in is the time this part was added to the buffer  - needed to flush old messages
            new_part_num = tagblock['tagblock_sentence']
            new_part = dict(part_num=new_part_num, line=line, index=index, time_in=now)

            buffered_parts = buffer[key]
            part_nums = set(part['part_num'] for part in buffered_parts)

            if new_part_num in part_nums:
                # already another message part with this part_num in the buffer, so flush out the unmatched parts
                for part in sorted(buffered_parts, key=lambda x: x['index']):
                    yield part['line']
                # replace the slot in the buffer with the new part
                buffer[key] = [new_part]

            elif part_nums.union({new_part_num}) == set(range(1, total_parts + 1)):
                # found all the parts.   Concatenate them in order and send the combined line out
                buffer[key].append(new_part)
                yield ''.join([part['line'] for part in sorted(buffer[key], key=lambda x:x['part_num'])])
                del buffer[key]

            else:
                buffer[key].append(new_part)

        # prepare to flush old parts from the buffer
        flush_keys = set()
        flush_time = now - (max_time_window / 1000)
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
