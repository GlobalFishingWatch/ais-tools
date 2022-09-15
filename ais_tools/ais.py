from ais_tools.transcode import DecodeError
from ais_tools import ais8
from ais_tools.transcode import ASCII8toAIS6
from ais_tools import ais18
from ais_tools import ais19
from ais_tools import ais24
from ais_tools import ais25


encode_fn = {
    8: ais8.ais8_encode,
    18: ais18.ais18_encode,
    19: ais19.ais19_encode,
    24: ais24.ais24_encode,
    25: ais25.ais25_encode,
}

decode_fn = {
    8: ais8.ais8_decode,
    18: ais18.ais18_decode,
    19: ais19.ais19_decode,
    24: ais24.ais24_decode,
    25: ais25.ais25_decode,
}


class AISMessageTranscoder:
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
        try:
            result = decode_fn[message_type](body, pad)
        except KeyError:
            raise DecodeError(f'No decode method available for message type {message_type}')

        return result
