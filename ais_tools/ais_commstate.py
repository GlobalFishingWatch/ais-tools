from ais_tools.transcode import DecodeError
from ais_tools.transcode import UintField as Uint
from ais_tools.transcode import BitField as Bits
from ais_tools.transcode import NmeaStruct as Struct
from ais_tools.transcode import BoolField as Bool


def ais_commstate_decode(bits, message):
    cs, fields = ais_commstate_fields(message)
    message.update(bits.unpack(fields))

    if cs == 'SOTDMA':
        fields = sotdma_timeout_fields(message)
        message.update(bits.unpack(fields))


def ais_commstate_encode(bits, message):
    cs, commstate_fields = ais_commstate_fields(message)
    timeout_fields = sotdma_timeout_fields(message)

    bits.pack(commstate_fields, message)
    if cs == 'SOTDMA':
        bits.pack(timeout_fields, message)


def ais_commstate_fields(message):
    if message.get('unit_flag', 0):
        return 'CS', ais_commstate_CS
    elif message.get('commstate_flag', 0):
        return 'ITDMA', ais_commstate_ITDMA
    else:
        return 'SOTDMA', ais_commstate_SOTDMA


def sotdma_timeout_fields(message):
    slot_timeout = message.get('slot_timeout', 0)
    if slot_timeout == 0:
        return ais_commstate_SOTDMA_timeout_0
    elif slot_timeout == 1:
        return ais_commstate_SOTDMA_timeout_1
    elif slot_timeout in (2, 4, 6):
        return ais_commstate_SOTDMA_timeout_2_4_6
    elif slot_timeout in (3, 5, 7):
        return ais_commstate_SOTDMA_timeout_3_5_7
    else:
        raise DecodeError(f'AIS18: unknown slot_timeout value {slot_timeout}')


ais_commstate_CS = Struct(
    Bits(name='commstate', nbits=19, default='1100000000000000110')
)

ais_commstate_ITDMA = Struct(
    Uint(name='sync_state', nbits=2, default=0),
    Uint(name='slot_increment', nbits=13, default=0),
    Uint(name='slots_to_allocate', nbits=3, default=0),
    Bool(name='keep_flag', nbits=1, default=0)
)

ais_commstate_SOTDMA = Struct(
    Uint(name='sync_state', nbits=2, default=0),
    Uint(name='slot_timeout', nbits=3, default=0),
)

ais_commstate_SOTDMA_timeout_0 = Struct(
    Uint(name='slot_offset', nbits=14, default=0),
)

ais_commstate_SOTDMA_timeout_1 = Struct(
    Uint(name='utc_hour', nbits=5, default=0),
    Uint(name='utc_min', nbits=7, default=0),
    Uint(name='utc_spare', nbits=2, default=0),
)

ais_commstate_SOTDMA_timeout_2_4_6 = Struct(
    Uint(name='slot_number', nbits=14, default=0),
)

ais_commstate_SOTDMA_timeout_3_5_7 = Struct(
    Uint(name='received_stations', nbits=14, default=0),
)
