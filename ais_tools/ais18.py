from ais_tools import transcode
from ais_tools.transcode import DecodeError
from ais_tools.transcode import BitsTranscoder
from ais_tools.transcode import UintTranscoder as Uint
from ais_tools.transcode import Uint10Transcoder as Uint10
from ais_tools.transcode import LatLonTranscoder as LatLon


class AIS18CommState(transcode.MessageTranscoder):

    def commstate_fields (self, unit_flag, commstate_flag, slot_timeout):
        if unit_flag:
            return ais18_commstate_CS
        elif commstate_flag:
            return ais18_commstate_ITDMA
        else:
            if slot_timeout == 0:
                return ais18_commstate_SOTDMA_timeout_0
            elif slot_timeout == 1:
                return ais18_commstate_SOTDMA_timeout_1
            elif slot_timeout in (2, 4, 6):
                return ais18_commstate_SOTDMA_timeout_2_4_6
            elif slot_timeout in (3, 5, 7):
                return ais18_commstate_SOTDMA_timeout_3_5_7
            else:
                raise DecodeError('AIS18: unknown slot_timeout value {}'.format(slot_timeout))

    def encode_fields(self, message):
        return self.commstate_fields (message.get('unit_flag'), message.get('commstate_flag'), message.get('slot_timeout'))

    def decode_fields(self, bits, message):
        return self.commstate_fields(
            message.get('unit_flag', bits[141:142].uint),
            message.get('commstate_flag', bits[148:149].uint),
            message.get('slot_timeout', bits[151:154].uint),
        )


ais18_fields = [
    Uint(name='id', nbits=6, default=0),
    Uint(name='repeat_indicator', nbits=2),
    Uint(name='mmsi', nbits=30),
    Uint(name='spare', nbits=8),
    Uint10(name='sog', nbits=10, default=102.3),
    Uint(name='position_accuracy', nbits=1),
    LatLon(name='x', nbits=28, default=181),
    LatLon(name='y', nbits=27, default=91),
    Uint10(name='cog', nbits=12, default=360),
    Uint(name='true_heading', nbits=9, default=511),
    Uint(name='timestamp', nbits=6, default=60),
    Uint(name='spare2', nbits=2),
    Uint(name='unit_flag', nbits=1),
    Uint(name='display_flag', nbits=1),
    Uint(name='dsc_flag', nbits=1),
    Uint(name='band_flag', nbits=1),
    Uint(name='m22_flag', nbits=1),
    Uint(name='mode_flag', nbits=1),
    Uint(name='raim', nbits=1),
    Uint(name='commstate_flag', nbits=1),
    AIS18CommState()
]

ais18_commstate_CS = [
    BitsTranscoder(name='commstate', nbits=19, default='1100000000000000110'),
]

ais18_commstate_ITDMA = [
    Uint(name='sync_state', nbits=2),
    Uint(name='slot_increment', nbits=13),
    Uint(name='slots_to_allocate', nbits=3),
    Uint(name='keep_flag', nbits=1),
]


ais18_commstate_SOTDMA_timeout_0 = [
    Uint(name='sync_state', nbits=2),
    Uint(name='slot_timeout', nbits=3),
    Uint(name='slot_offset', nbits=14),
]

ais18_commstate_SOTDMA_timeout_1 = [
    Uint(name='sync_state', nbits=2),
    Uint(name='slot_timeout', nbits=3),
    Uint(name='utc_hour', nbits=5),
    Uint(name='utc_min', nbits=7),
    Uint(name='utc_spare', nbits=2),
]

ais18_commstate_SOTDMA_timeout_2_4_6 = [
    Uint(name='sync_state', nbits=2),
    Uint(name='slot_timeout', nbits=3),
    Uint(name='slot_number', nbits=14),
]

ais18_commstate_SOTDMA_timeout_3_5_7 = [
    Uint(name='sync_state', nbits=2),
    Uint(name='slot_timeout', nbits=3),
    Uint(name='received_stations', nbits=14),
]
