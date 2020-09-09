from ais_tools import transcode
from ais_tools.transcode import DecodeError
from ais_tools.transcode import UintTranscoder as Uint
from ais_tools.transcode import ASCII6Transcoder as ASCII6
from ais_tools.transcode import VariableLengthASCII6Transcoder as VarASCII6

# Using this coding  http://www.e-navigation.nl/content/text-using-6-bit-ascii-1


class AIS25Transcoder(transcode.MessageTranscoder):
    def __init__(self):
        super().__init__(ais25_fields)


class AIS25Destination(transcode.MessageTranscoder):
    def get_fields(self, message=None):
        addressed = message.get('addressed', 0)
        if addressed:
            return ais25_destination_fields
        else:
            return []


ais25_fields = [
    Uint(name='repeat_indicator', nbits=2),
    Uint(name='mmsi', nbits=30),
    Uint(name='part_num', nbits=2),
    Uint(name='addressed', nbits=1),
    Uint(name='use_app_id', nbits=1),
    AIS25Destination(),
    Uint(name='dac', nbits=10, default=1),
    Uint(name='fi', nbits=6),
    Uint(name='text_seq', nbits=11),
    VarASCII6(name='text', default='')
]

ais25_destination_fields = [
    Uint(name='dest_mmsi', nbits=30),
    Uint(name='spare', nbits=2),
]







