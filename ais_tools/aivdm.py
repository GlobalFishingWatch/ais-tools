"""
Tools for decoding AIS messages in AIVDM format
"""

import json
import re
from datetime import datetime

import ais as libais
from ais import DecodeError
# import warnings
# with warnings.catch_warnings():
#     warnings.simplefilter("ignore")
#     from ais import stream as libais_stream

from ais_tools.ais import AISMessageTranscoder
from ais_tools.nmea import split_multipart
from ais_tools.nmea import expand_nmea
from ais_tools.tagblock import isChecksumValid
from ais_tools.tagblock import parseTagBlock


class LibaisDecoder:
    @staticmethod
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
        return msg

    @staticmethod
    def decode_payload(body, pad):
        res = libais.decode(body, pad)
        return LibaisDecoder.validate_field_types(res)


class AisToolsDecoder:
    def __init__(self):
        self.transcoder = AISMessageTranscoder()

    def decode_payload(self, body, pad):
        aistools_err = None
        try:
            return self.transcoder.decode_nmea(body, pad)
        except DecodeError as e:
            libais_err = str(e)

        try:
            return LibaisDecoder.decode_payload(body, pad)
        except DecodeError as e:
            raise DecodeError('AISTOOLS ERR: {}  LIBAIS ERR: {}'.format(aistools_err, str(e)))


class AisToolsEncoder:
    def __init__(self):
        self.transcoder = AISMessageTranscoder()

    def encode_payload(self, message):
        return self.transcoder.encode_nmea(message)


class AIVDM:
    def __init__(self, decoder=None, encoder=None):
        self.decoder = decoder or AisToolsDecoder()
        self.encoder = encoder or AisToolsEncoder()

    def safe_decode(self, nmea):
        msg = {}
        try:
            msg = self.decode(nmea)
        except libais.DecodeError as e:
            msg = dict(
                nmea=nmea,
                error=str(e)
            )
        return msg

    def decode(self, nmea):

        msg = dict(nmea=nmea)
        parts = [expand_nmea(part) for part in split_multipart(nmea)]
        if len(parts) == 0:
            raise DecodeError('No valid AIVDM found in {}'.format(nmea))
        elif len(parts) == 1:
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

        # Check to see if a multipart message is missing some parts, or maybe has extra
        if len(parts) != tagblock['tagblock_groupsize']:
            raise DecodeError(
                'Expected {} message parts to decode but found {}'.format(tagblock['tagblock_groupsize'], len(parts))
            )

        msg.update(tagblock)
        msg.update(self.decode_payload(body, pad))

        return msg

    def decode_stream(self, lines):
        for line in lines:
            yield self.decode(line)

    def decode_payload(self, body, pad):
        return self.decoder.decode_payload(body, pad)

    # def expand_nmea(line):
    #     try:
    #         tagblock, nmea = parseTagBlock(line)
    #     except ValueError as e:
    #         raise DecodeError('Failed to parse tagblock (%s) %s' % (str(e), line))
    #
    #     nmea = nmea.strip()
    #     fields = nmea.split(',')
    #     if len(fields) < 6:
    #         raise DecodeError('not enough fields in nmea message')
    #
    #     if not isChecksumValid(nmea):
    #         raise DecodeError('Invalid checksum')
    #
    #     try:
    #         tagblock['tagblock_groupsize'] = int(fields[1])
    #         tagblock['tagblock_sentence'] = int(fields[2])
    #         if fields[3] != '':
    #             tagblock['tagblock_id'] = int(fields[3])
    #         tagblock['tagblock_channel'] = fields[4]
    #         body = fields[5]
    #         pad = int(nmea.split('*')[0][-1])
    #     except ValueError:
    #         raise DecodeError('Unable to convert field to int in nmea message')
    #
    #     if 'tagblock_group' in tagblock:
    #         tagblock_group = tagblock.get('tagblock_group', {})
    #         del tagblock['tagblock_group']
    #         group_fields = {'tagblock_' + k: v for k, v in tagblock_group.items()}
    #         tagblock.update(group_fields)
    #
    #     return tagblock, body, pad


# def split_multipart(line):
#     """
#     Split a single line of text that contains one or more nmea messages
#     Expects the combined lines to have been joined with join_multipart()
#
#     Each message part is expected to be one of these
#         !AIDVM....
#         \\!AIDVM....
#         \\tagblock\\!AIDVM....
#
#     and all parts in the line should have the same format
#     """
#     if line.startswith('!'):
#         regex = r'(![^!]+)'
#     elif line.startswith('\\!'):
#         regex = r'(\\![^!\\]+)'
#     elif line.startswith('\\'):
#         regex = r'(\\[^\\]+\\![^!\\]+)'
#     else:
#         raise libais.DecodeError('no valid AIVDM message detected')
#
#     return re.findall(regex, line)
#
#
# def join_multipart(lines):
#     """
#     takes a list of nmea text lines that form a single mulitpart message and concatenates them in the order given
#     """
#     start_chars = {line[0] for line in lines}
#     if len(start_chars) == 1 and start_chars.issubset({'\\', '!'}):
#         return ''.join(lines)
#     raise DecodeError("all lines to be joined must start with the same character, either '\\' or '!'")
#
#
# def safe_join_multipart_stream(lines, max_time_window=2, max_message_window=1000):
#     """
#     Same as join_multipart_stream but for any message that cannot decoded, it will just emit
#     that message back out and not raise a DecodeError exception
#     """
#     lines = join_multipart_stream(
#             lines,
#             max_time_window=max_time_window,
#             max_message_window=max_message_window,
#             ignore_decode_errors=True
#             )
#     for line in lines:
#         yield line
#
#
# def join_multipart_stream(lines, max_time_window=2, max_message_window=1000, ignore_decode_errors=False):
#     """
#     Takes a stream of nmea text lines and tries to find the matching parts of multi part messages
#     which may not be adjacent in the stream and may come out of order.
#
#     Matched message parts will be concatenated together into a single line using join_multipart()
#     All other messages will come out with no changes
#     """
#     buffer = defaultdict(list)
#
#     for index, line in enumerate(lines):
#         try:
#             tagblock, body, pad = AIVDM.expand_nmea(line)
#         except libais.DecodeError:
#             if ignore_decode_errors:
#                 yield line
#                 continue
#             else:
#                 raise
#
#         now = datetime.utcnow().timestamp()
#         if tagblock['tagblock_groupsize'] == 1:
#             # this is a single part part message, so nothing to do, just pass it out
#             yield line
#         else:
#             # make a key for matching message parts
#             # - tagblock_groupsize is the number of parts we are looking for
#             # - tagblock_station is the source of the message and may not have a value
#             # - tagblock_id is a sequence number that is the same for all message parts, but it is not unique
#             # - tagblock_channel is the AIS RF channel (either A or B) that was used for transmission
#             key = (tagblock.get('tagblock_groupsize'), tagblock.get('tagblock_station'),
#                    tagblock.get('tagblock_id'), tagblock.get('tagblock_channel'))
#
#             # pack up the message part
#             # - tagblock_sentence is the index of this part relative to the other parts, where the first part is 1
#             # - line is the nmea that was passed in
#             # - index is the index of this line in the stream - needed to flush old messages
#             # - time_in is the time this part was added to the buffer  - needed to flush old messages
#             part = dict(part_num=tagblock['tagblock_sentence'], line=line, index=index, time_in=now)
#
#             buffered_part_nums = set(part['part_num'] for part in buffer[key])
#             if part['part_num'] in buffered_part_nums:
#                 # already another message part with this part_num in the buffer, so flush out the unmatched parts
#                 for part in sorted(buffer[key], key=lambda x: x['index']):
#                     yield part['line']
#                 # replace the slot in the buffer with the new part
#                 buffer[key] = [part]
#
#             elif buffered_part_nums.union({tagblock['tagblock_sentence']}) == set(range(1, tagblock['tagblock_groupsize'] + 1)):
#                 # found all the parts.   Concatenate them in order and send the combined line out
#                 buffer[key].append(part)
#                 yield ''.join([part['line'] for part in sorted(buffer[key], key=lambda x:x['part_num'])])
#                 del buffer[key]
#
#             else:
#                 buffer[key].append(part)
#
#         # prepare to flush old parts from the buffer
#         flush_keys = set()
#         flush_time = now - max_time_window
#         flush_index = index - max_message_window
#
#         # find any keys that have at least one part that is too old
#         for key, parts in buffer.items():
#             if any(part['time_in'] < flush_time or part['index'] < flush_index for part in parts):
#                 flush_keys.add(key)
#
#         # flush out all the unmatched parts for all keys that have at least one old part.
#         # Send them out in the order they arrived
#         flush_parts = []
#         for key in flush_keys:
#             flush_parts += buffer[key]
#             del buffer[key]
#         for part in sorted(flush_parts, key=lambda x: x['index']):
#             yield part['line']
#
#     # input stream ended, so flush whatever parts are left in the buffer in the order they arrived
#     for key, parts in buffer.items():
#         for part in sorted(parts, key=lambda x: x['index']):
#             yield part['line']
#
