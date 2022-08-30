from ais_tools import transcode
from ais_tools.transcode import DecodeError
from ais_tools.transcode import BitsTranscoder
from ais_tools.transcode import UintTranscoder as _Uint
from ais_tools.transcode import BooleanTranscoder as _Bool
from ais_tools.transcode import Uint10Transcoder as _Uint10
from ais_tools.transcode import LatLonTranscoder as _LatLon

from ais_tools.transcode import NmeaBits
from ais_tools.transcode import NmeaStruct as Struct
from ais_tools.transcode import UintField as Uint
from ais_tools.transcode import Uint10Field as Uint10
from ais_tools.transcode import LatLonField as LatLon
from ais_tools.transcode import BoolField as Bool
from ais_tools.transcode import BitField as Bits


def ais18_decode(body, pad):
    bits = NmeaBits.from_nmea(body, pad)
    message = bits.unpack(ais18_fields)

    cs, fields = ais18_commstate_fields(message)
    message.update(bits.unpack(fields))

    if cs == 'SOTDMA':
        fields = sotdma_timeout_fields(message)
        message.update(bits.unpack(fields))

    return message


def ais18_encode(message):
    bits = NmeaBits(ais18_fields.nbits + ais18_commstate_CS.nbits)
    bits.pack(ais18_fields, message)

    cs, fields = ais18_commstate_fields(message)
    bits.pack(fields, message)

    if cs == 'SOTDMA':
        fields = sotdma_timeout_fields(message)
        bits.pack(fields, message)

    return bits.to_nmea()


def ais18_commstate_fields(message):
    if message['unit_flag']:
        return 'CS', ais18_commstate_CS
    elif message['commstate_flag']:
        return 'ITDMA', ais18_commstate_ITDMA
    else:
        return 'SOTDMA', ais18_commstate_SOTDMA


def sotdma_timeout_fields(message):
    slot_timeout = message['slot_timeout']
    if slot_timeout == 0:
        return ais18_commstate_SOTDMA_timeout_0
    elif slot_timeout == 1:
        return ais18_commstate_SOTDMA_timeout_1
    elif slot_timeout in (2, 4, 6):
        return ais18_commstate_SOTDMA_timeout_2_4_6
    elif slot_timeout in (3, 5, 7):
        return ais18_commstate_SOTDMA_timeout_3_5_7
    else:
        raise DecodeError(f'AIS18: unknown slot_timeout value {slot_timeout}')


ais18_fields = Struct(
    Uint(name='id', nbits=6, default=18),
    Uint(name='repeat_indicator', nbits=2),
    Uint(name='mmsi', nbits=30),
    Uint(name='spare', nbits=8, default=0),
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
    Bool(name='raim', nbits=1),
    Uint(name='commstate_flag', nbits=1)
)


ais18_commstate_CS = Struct(
    Bits(name='commstate', nbits=19, default='1100000000000000110')
)

ais18_commstate_ITDMA = Struct(
    Uint(name='sync_state', nbits=2),
    Uint(name='slot_increment', nbits=13),
    Uint(name='slots_to_allocate', nbits=3),
    Bool(name='keep_flag', nbits=1)
)

ais18_commstate_SOTDMA = Struct(
    Uint(name='sync_state', nbits=2),
    Uint(name='slot_timeout', nbits=3),
)

ais18_commstate_SOTDMA_timeout_0 = Struct(
    Uint(name='slot_offset', nbits=14),
)

ais18_commstate_SOTDMA_timeout_1 = Struct(
    Uint(name='utc_hour', nbits=5),
    Uint(name='utc_min', nbits=7),
    Uint(name='utc_spare', nbits=2),
)

ais18_commstate_SOTDMA_timeout_2_4_6 = Struct(
    Uint(name='slot_number', nbits=14),
)

ais18_commstate_SOTDMA_timeout_3_5_7 = Struct(
    Uint(name='received_stations', nbits=14),
)


class AIS18CommState(transcode.MessageTranscoder):

    def commstate_fields(self, unit_flag, commstate_flag, slot_timeout):
        if unit_flag:
            return _ais18_commstate_CS
        elif commstate_flag:
            return _ais18_commstate_ITDMA
        else:
            if slot_timeout == 0:
                return _ais18_commstate_SOTDMA_timeout_0
            elif slot_timeout == 1:
                return _ais18_commstate_SOTDMA_timeout_1
            elif slot_timeout in (2, 4, 6):
                return _ais18_commstate_SOTDMA_timeout_2_4_6
            elif slot_timeout in (3, 5, 7):
                return _ais18_commstate_SOTDMA_timeout_3_5_7
            else:
                raise DecodeError('AIS18: unknown slot_timeout value {}'.format(slot_timeout))

    def encode_fields(self, message):
        return self.commstate_fields(message.get('unit_flag'), message.get('commstate_flag'), message.get('slot_timeout'))

    def decode_fields(self, bits, message):
        return self.commstate_fields(
            message.get('unit_flag', bits[141:142].uint),
            message.get('commstate_flag', bits[148:149].uint),
            message.get('slot_timeout', bits[151:154].uint),
        )


_ais18_fields = [
    _Uint(name='id', nbits=6, default=0),
    _Uint(name='repeat_indicator', nbits=2),
    _Uint(name='mmsi', nbits=30),
    _Uint(name='spare', nbits=8),
    _Uint10(name='sog', nbits=10, default=102.3),
    _Uint(name='position_accuracy', nbits=1),
    _LatLon(name='x', nbits=28, default=181),
    _LatLon(name='y', nbits=27, default=91),
    _Uint10(name='cog', nbits=12, default=360),
    _Uint(name='true_heading', nbits=9, default=511),
    _Uint(name='timestamp', nbits=6, default=60),
    _Uint(name='spare2', nbits=2),
    _Uint(name='unit_flag', nbits=1),
    _Uint(name='display_flag', nbits=1),
    _Uint(name='dsc_flag', nbits=1),
    _Uint(name='band_flag', nbits=1),
    _Uint(name='m22_flag', nbits=1),
    _Uint(name='mode_flag', nbits=1),
    _Bool(name='raim', nbits=1),
    _Uint(name='commstate_flag', nbits=1),
    AIS18CommState()
]

_ais18_commstate_CS = [
    BitsTranscoder(name='commstate', nbits=19, default='1100000000000000110'),
]

_ais18_commstate_ITDMA = [
    _Uint(name='sync_state', nbits=2),
    _Uint(name='slot_increment', nbits=13),
    _Uint(name='slots_to_allocate', nbits=3),
    _Bool(name='keep_flag', nbits=1),
]


_ais18_commstate_SOTDMA_timeout_0 = [
    _Uint(name='sync_state', nbits=2),
    _Uint(name='slot_timeout', nbits=3),
    _Uint(name='slot_offset', nbits=14),
]

_ais18_commstate_SOTDMA_timeout_1 = [
    _Uint(name='sync_state', nbits=2),
    _Uint(name='slot_timeout', nbits=3),
    _Uint(name='utc_hour', nbits=5),
    _Uint(name='utc_min', nbits=7),
    _Uint(name='utc_spare', nbits=2),
]

_ais18_commstate_SOTDMA_timeout_2_4_6 = [
    _Uint(name='sync_state', nbits=2),
    _Uint(name='slot_timeout', nbits=3),
    _Uint(name='slot_number', nbits=14),
]

_ais18_commstate_SOTDMA_timeout_3_5_7 = [
    _Uint(name='sync_state', nbits=2),
    _Uint(name='slot_timeout', nbits=3),
    _Uint(name='received_stations', nbits=14),
]
