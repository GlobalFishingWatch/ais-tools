from ais_tools.transcode import DecodeError
from ais_tools.transcode import MessageTranscoder
from ais_tools.transcode import bits_to_nmea
from ais_tools.transcode import nmea_to_bits
from ais_tools.transcode import byte_align
from ais_tools import ais8
from ais_tools.transcode import ASCII8toAIS6
from ais_tools import ais18
from ais_tools import ais24
from ais_tools import ais25


message_types = {
    8: ais8._ais8_fields,
    18: ais18._ais18_fields,
    24: [ais24.AIS24Transcoder()],
    25: ais25._ais25_fields,
}

encode_fn = {
    8: ais8.ais8_encode,
    18: ais18.ais18_encode,
    24: ais24.ais24_encode,
    25: ais25.ais25_encode,
}

decode_fn = {
    8: ais8.ais8_decode,
    18: ais18.ais18_decode,
    24: ais24.ais24_decode,
    25: ais25.ais25_decode,
}


class NewAISMessageTranscoder:
    @staticmethod
    def can_encode(message):
        return message.get('id') in encode_fn

    @staticmethod
    def can_decode(body, pad=0):
        return True if body and ASCII8toAIS6.get(body[0]) in decode_fn else False

    @staticmethod
    def encode_nmea(message):
        message_type = message.get('id')
        return encode_fn[message_type](message)

    @staticmethod
    def decode_nmea(body, pad=0):
        message_type = ASCII8toAIS6.get(body[0])
        return decode_fn[message_type](body, pad)



class AISMessageTranscoder(MessageTranscoder):

    def message_type_fields(self, msg_type):
        if msg_type not in message_types:
            raise DecodeError('AIS: Unknown message type {}'.format(msg_type))
        return message_types.get(msg_type, [])

    def encode_fields(self, message):
        return self.message_type_fields(message.get('id'))

    def decode_fields(self, bits, message):
        return self.message_type_fields(message.get('id', bits[0:6].uint))

    def encode_nmea(self, message):
        return bits_to_nmea(byte_align(self.encode(message)))

    def decode_nmea(self, body, pad=0):
        return self.decode(nmea_to_bits(body, pad))

    @staticmethod
    def can_encode(message):
        return message.get('id') in message_types

    @staticmethod
    def can_decode(body, pad=0):
        return True if body and ASCII8toAIS6.get(body[0]) in message_types else False
