"""
Tools for decoding AIS messages in AIVDM format
"""

import json
from datetime import datetime

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


def decode_nmea_body(body, pad):
    try:
        return libais.decode(body, pad)
    except libais.DecodeError as e:
        # Special case for issue #1 - some type 24 messages have incorrect length

        if str(e) == 'Ais24: AIS_ERR_BAD_BIT_COUNT' and len(body) == 27:
            body = body + '0'
        else:
            raise
    return libais.decode(body, pad)


def decode_message(line):

    msg = dict(nmea=line)

    try:
        tagblock, nmea = libais_stream.parseTagBlock(line)
        msg.update(tagblock)

        if not libais_stream.checksum.isChecksumValid(nmea):
            raise libais.DecodeError('Invalid checksum')

        # TODO: handle multi-sentence messages
        fields = nmea.split(',')
        assert int(fields[1]) == 1, 'must be a single sentence message'

        body = fields[5]
        pad = int(nmea.split('*')[0][-1])
        # print(body, pad)
        msg.update(decode_nmea_body(body, pad))

    except libais.DecodeError as e:
        msg['error'] = str(e)

    return msg


def decode_stream(lines):
    for line in lines:
        yield decode_message(line)


def format_messages(messages, fmt):
    for msg in messages:
        yield json.dumps(msg)
