"""
Tools for decoding AIS messages in AIVDM format
"""

from __future__ import annotations

import ais as libais
from ais import DecodeError

from ais_tools.ais import AISMessageTranscoder
from ais_tools.nmea import split_multipart
from ais_tools.nmea import expand_nmea
from ais_tools.core import checksum_str
from ais_tools.message import Message


class LibaisDecoder:
    @staticmethod
    def validate_field_types(msg: dict) -> dict:
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
    def decode_payload(body: str, pad: int) -> dict:
        res = libais.decode(body, pad)
        return LibaisDecoder.validate_field_types(res)


class AisToolsDecoder:
    def __init__(self):
        self.transcoder = AISMessageTranscoder()

    def decode_payload(self, body: str, pad: int) -> dict:
        aistools_err = None

        if self.transcoder.can_decode(body, pad):
            try:
                return self.transcoder.decode_nmea(body, pad)
            except DecodeError as e:
                aistools_err = str(e)

        try:
            return LibaisDecoder.decode_payload(body, pad)
        except DecodeError as e:
            raise DecodeError('AISTOOLS ERR: {}  LIBAIS ERR: {}'.format(aistools_err, str(e)))


class AisToolsEncoder:
    def __init__(self):
        self.transcoder = AISMessageTranscoder()

    def encode_payload(self, message: dict) -> tuple[str, int]:
        if not self.transcoder.can_encode(message):
            raise DecodeError(f'AISTOOLS ERR: Failed to encode unknown message type {message.get("id")}')

        return self.transcoder.encode_nmea(message)


class AIVDM:
    """
    AIVDM message encoder/decoder

    On construction, pass in the encoder and decoder to use
    """
    def __init__(self, decoder: AisToolsDecoder | None = None, encoder: AisToolsEncoder | None = None) -> None:
        self.decoder = decoder or AisToolsDecoder()
        self.encoder = encoder or AisToolsEncoder()

    def safe_decode(self, nmea: str, best_effort: bool = False) -> Message:
        """
        Attempt to decode an AIVDM message using AIVDM.decode().   If a error occurs and DecodeError is raised,
        suppress the exception and instead return a dict:

        {
          "nmea": [original nmea string passed in],
          "error": [Decode error message]
        }
        """
        msg = Message(nmea)
        try:
            msg = self.decode(nmea, safe_decode_payload=best_effort)
        except libais.DecodeError as e:
            msg['error'] = str(e)
        return msg

    def decode(self, nmea: str, safe_decode_payload: bool = False, validate_checksum: bool = False) -> Message:
        """
        Decode a single line of nmea that contains:
            a single-part AIVDM message, with or without prepended tagblock
            or a concatenated set of AIVDM messages that make up the parts for a multi-part message
        Returns a dict with the passed in nmea string in the "nmea" field

        raises DecodeError if the message cannot be decoded.
        """

        msg = Message(nmea)
        nmea = msg.nmea
        parts = [expand_nmea(part, validate_checksum=validate_checksum) for part in split_multipart(nmea)]
        if len(parts) == 0:
            raise DecodeError('No valid AIVDM found in {}'.format(nmea))
        elif len(parts) == 1:
            # single part message
            tagblock, body, pad = parts[0]
        else:
            # multipart message
            parts = sorted(parts, key=lambda x: x[0]['tagblock_sentence'])
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

        try:
            # Check to see if a multipart message is missing some parts, or maybe has extra
            if len(parts) != tagblock['tagblock_groupsize']:
                raise DecodeError(
                    'Expected {} message parts to decode but found {}'.format(tagblock['tagblock_groupsize'], len(parts))
                )

            msg.update(self.decode_payload(body, pad))
        except DecodeError as e:
            if safe_decode_payload:
                msg['error'] = str(e)
            else:
                raise

        return msg

    def decode_payload(self, body: str, pad: int) -> dict:
        """
        decode just the payload part of an AIVDM message

        For example, in this nmea message
            !AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49
        the body is in field 5
            15NTES0P00J>tC4@@FOhMgvD0D0M
        and pad is in field 6
            0
        """
        return self.decoder.decode_payload(body, pad)

    def safe_encode(self, message: dict) -> Message:
        try:
            return self.encode(message)
        except DecodeError as e:
            msg = self.encode(Message(id=25, mmsi=0, text='ERROR'))
            msg['error'] = str(e)
            return msg

    def encode(self, message: dict) -> Message:
        body, pad = self.encode_payload(message)
        sentence = "AIVDM,1,1,,A,{},{}".format(body, pad)
        return Message("!{}*{}".format(sentence, checksum_str(sentence)))

    def encode_payload(self, message: dict) -> tuple[str, int]:
        return self.encoder.encode_payload(message)
