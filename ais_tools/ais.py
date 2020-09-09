from ais_tools.transcode import DecodeError
from ais_tools.transcode import MessageTranscoder
from ais_tools.transcode import UintTranscoder as Uint
from ais_tools.transcode import bits_to_nmea
from ais_tools.transcode import nmea_to_bits
from ais_tools.transcode import byte_align
from ais_tools import ais18
from ais_tools import ais24
from ais_tools import ais25


message_types = {
    18: [ais18.AIS18Transcoder()],
    24: [ais24.AIS24Transcoder()],
    25: [ais25.AIS25Transcoder()],
}


class AISMessageTypeTranscoder(MessageTranscoder):

    def get_fields(self, message=None):
        msg_type = message.get('id')
        if msg_type not in message_types:
            raise DecodeError('AIS: Unknown message type {}'.format(msg_type))
        fields = message_types.get(msg_type, [])
        return fields


ais_fields = [
    Uint(name='id', nbits=6, default=0),
    AISMessageTypeTranscoder(),
]


class AISMessageTranscoder(MessageTranscoder):
    def __init__(self):
        super().__init__(ais_fields)

    def encode_nmea(self, message):
        return bits_to_nmea(byte_align(self.encode(message)))

    def decode_nmea(self, body, pad=0):
        return self.decode(nmea_to_bits(body, pad))
