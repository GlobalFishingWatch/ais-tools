"""
Tools for decoding AIS messages in AIVDM format
"""

import json
import ais as libais
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from ais import stream as libais_stream


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


def decode_message(line):

    msg = dict()

    try:
        tagblock, nmea = libais_stream.parseTagBlock(line)
        msg.update(tagblock)
        msg['nmea'] = nmea

        if not libais_stream.checksum.isChecksumValid(nmea):
            raise libais.DecodeError('Invalid checksum')

        # TODO: handle multi-sentence messages
        fields = nmea.split(',')
        assert int(fields[1]) == 1, 'must be a single sentence message'

        body = fields[5]
        pad = int(nmea.split('*')[0][-1])
        # print(body, pad)
        msg.update(libais.decode(body, pad))

    except libais.DecodeError as e:
        msg['error'] = str(e)

    return msg


def decode_stream(lines):
    for line in lines:
        yield decode_message(line)


def format_messages(messages, fmt):
    for msg in messages:
        yield json.dumps(msg)
