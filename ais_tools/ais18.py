from ais_tools.transcode import DecodeError
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

    cs, commstate_fields = ais18_commstate_fields(message)
    timeout_fields = sotdma_timeout_fields(message)

    bits.pack(commstate_fields, message)
    if cs == 'SOTDMA':
        bits.pack(timeout_fields, message)

    return bits.to_nmea()


def ais18_commstate_fields(message):
    if message.get('unit_flag', 0):
        return 'CS', ais18_commstate_CS
    elif message.get('commstate_flag', 0):
        return 'ITDMA', ais18_commstate_ITDMA
    else:
        return 'SOTDMA', ais18_commstate_SOTDMA


def sotdma_timeout_fields(message):
    slot_timeout = message.get('slot_timeout', 0)
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
    Uint(name='repeat_indicator', nbits=2, default=0),
    Uint(name='mmsi', nbits=30),
    Uint(name='spare', nbits=8, default=0),
    Uint10(name='sog', nbits=10, default=102.3),
    Uint(name='position_accuracy', nbits=1, default=0),
    LatLon(name='x', nbits=28, default=181),
    LatLon(name='y', nbits=27, default=91),
    Uint10(name='cog', nbits=12, default=360),
    Uint(name='true_heading', nbits=9, default=511),
    Uint(name='timestamp', nbits=6, default=60),
    Uint(name='spare2', nbits=2, default=0),
    Uint(name='unit_flag', nbits=1, default=0),
    Uint(name='display_flag', nbits=1, default=0),
    Uint(name='dsc_flag', nbits=1, default=0),
    Uint(name='band_flag', nbits=1, default=0),
    Uint(name='m22_flag', nbits=1, default=0),
    Uint(name='assigned_mode', nbits=1, default=0),  # NB: Libais calls this 'mode_flag" for type 18, and calls it
                                                     # 'assigned_mode' for 19 and 21.
    Bool(name='raim', nbits=1, default=0),
    Uint(name='commstate_flag', nbits=1, default=0)
)


ais18_commstate_CS = Struct(
    Bits(name='commstate', nbits=19, default='1100000000000000110')
)

ais18_commstate_ITDMA = Struct(
    Uint(name='sync_state', nbits=2, default=0),
    Uint(name='slot_increment', nbits=13, default=0),
    Uint(name='slots_to_allocate', nbits=3, default=0),
    Bool(name='keep_flag', nbits=1, default=0)
)

ais18_commstate_SOTDMA = Struct(
    Uint(name='sync_state', nbits=2, default=0),
    Uint(name='slot_timeout', nbits=3, default=0),
)

ais18_commstate_SOTDMA_timeout_0 = Struct(
    Uint(name='slot_offset', nbits=14, default=0),
)

ais18_commstate_SOTDMA_timeout_1 = Struct(
    Uint(name='utc_hour', nbits=5, default=0),
    Uint(name='utc_min', nbits=7, default=0),
    Uint(name='utc_spare', nbits=2, default=0),
)

ais18_commstate_SOTDMA_timeout_2_4_6 = Struct(
    Uint(name='slot_number', nbits=14, default=0),
)

ais18_commstate_SOTDMA_timeout_3_5_7 = Struct(
    Uint(name='received_stations', nbits=14, default=0),
)
