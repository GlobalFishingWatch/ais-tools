from ais_tools.transcode import MessageTranscoder as Message
from ais_tools.transcode import DecodeError
from ais_tools.transcode import UintTranscoder as _Uint
from ais_tools.transcode import ASCII6Transcoder as _ASCII6

from ais_tools.transcode import NmeaBits
from ais_tools.transcode import NmeaStruct as Struct
from ais_tools.transcode import UintField as Uint
from ais_tools.transcode import ASCII6Field as ASCII6



def ais24_decode(body, pad):
    bits = NmeaBits.from_nmea(body, pad)
    message = bits.unpack(ais24_fields)

    part_num = message['part_num']
    if part_num == 0:
        name = bits.unpack(ais24_part_A_fields)
        message['name'] = name['name_1'] + name['name_2']
    elif part_num == 1:
        message.update(bits.unpack(ais24_part_B_fields))
    else:
        raise DecodeError(f'AIS24: unknown part number {part_num}')

    message.update(bits.unpack_from(vendorid_1371_4, offset=48))
    if message['mmsi'] // 10000000 == 98:
        message.update(bits.unpack_from(mothership_fields, offset=132))

    return message


def ais24_encode(message):
    part_num = message['part_num']
    if part_num == 0:
        nbits = 160
    elif part_num == 1:
        nbits = 168
    else:
        raise DecodeError(f'AIS24: unknown part number {part_num}')

    bits = NmeaBits(nbits)
    bits.pack(ais24_fields, message)
    if part_num == 0:
        name = {
            'name_1': message['name'][:10],
            'name_2': message['name'][10:],
        }
        bits.pack(ais24_part_A_fields, name)
    else:
        bits.pack(ais24_part_B_fields, message)

    if 'vendor_id' in message:
        bits.pack_into(vendorid_1371_4, offset=48, message=message)

    if 'mothership_mmsi' in message:
        bits.pack_into(mothership_fields, offset=132, message=message)

    return bits.to_nmea()


ais24_fields = Struct(
    Uint(name='id', nbits=6, default=0),
    Uint(name='repeat_indicator', nbits=2),
    Uint(name='mmsi', nbits=30),
    Uint(name='part_num', nbits=2)
)

ais24_part_A_fields = Struct(
    ASCII6(name='name_1', nbits=60),
    ASCII6(name='name_2', nbits=60)
)

ais24_part_B_fields = Struct(
    Uint(name='type_and_cargo', nbits=8),
    ASCII6(name='vendor_id', nbits=42, default='@@@@@@@'),
    ASCII6(name='callsign', nbits=42, default='@@@@@@@'),
    Uint(name='dim_a', nbits=9),
    Uint(name='dim_b', nbits=9),
    Uint(name='dim_c', nbits=6),
    Uint(name='dim_d', nbits=6),
    Uint(name='gps_type', nbits=4),
    Uint(name='spare', nbits=2)
)

vendorid_1371_4 = Struct(
    ASCII6(name='vendor_id_1371_4', nbits=18, default='@@@'),
    Uint(name='vendor_model', nbits=4),
    Uint(name='vendor_serial', nbits=20),

)

mothership_fields = Struct(
    Uint(name='mothership_mmsi', nbits=30),
)



class AIS24Transcoder(Message):

    def part_AB_fields(self, part_num):
        if part_num == 0:
            return _ais24_part_A_fields
        elif part_num == 1:
            return _ais24_part_B_fields
        else:
            raise DecodeError('AIS24: unknown part number {}'.format(part_num))

    def encode_fields(self, message):
        return self.part_AB_fields(message.get('part_num'))

    def decode_fields(self, bits, message):
        return self.part_AB_fields(message.get('part_num', bits[38:40].uint))


class VendorID(Message):
    def __init__(self, vendorid_1371_2, vendorid_1371_4):
        self.vendorid_1371_2 = vendorid_1371_2
        self.vendorid_1371_4 = vendorid_1371_4

    def encode_fields(self, message):
        if 'vendor_id' in message:
            return self.vendorid_1371_2
        else:
            return self.vendorid_1371_4

    def decode(self, bits, message=None):
        message = message or {}
        pos = bits.pos
        for d in self.vendorid_1371_2:
            message.update(d.decode(bits, message))
        bits.pos = pos  # reset read position to read the same bits again for multiple decoders
        for d in self.vendorid_1371_4:
            message.update(d.decode(bits, message))
        return message


class DimensionOrMothership(Message):
    def __init__(self, dim_fields, mothership_fields):
        super().__init__()
        self.dim_fields = dim_fields
        self.mothership_fields = mothership_fields

    def get_fields(self, message=None):
        mmsi = message.get('mmsi')
        if mmsi // 10000000 == 98:
            return self.mothership_fields
        else:
            return self.dim_fields


# PART A
_ais24_part_A_fields = [
    _Uint(name='id', nbits=6, default=0),
    _Uint(name='repeat_indicator', nbits=2),
    _Uint(name='mmsi', nbits=30),
    _Uint(name='part_num', nbits=2),
    _ASCII6(name='name', nbits=120),
]


_ais24_part_B_fields = [
    _Uint(name='id', nbits=6, default=0),
    _Uint(name='repeat_indicator', nbits=2),
    _Uint(name='mmsi', nbits=30),
    _Uint(name='part_num', nbits=2),
    _Uint(name='type_and_cargo', nbits=8),
    VendorID(
        [
            _ASCII6(name='vendor_id', nbits=42, default='@@@@@@@'),
        ],
        [
            _ASCII6(name='vendor_id_1371_4', nbits=18, default='@@@'),
            _Uint(name='vendor_model', nbits=4),
            _Uint(name='vendor_serial', nbits=20),
        ],
    ),
    _ASCII6(name='callsign', nbits=42, default='@@@@@@@'),
    DimensionOrMothership(
        [
            _Uint(name='dim_a', nbits=9),
            _Uint(name='dim_b', nbits=9),
            _Uint(name='dim_c', nbits=6),
            _Uint(name='dim_d', nbits=6),
        ],
        [
            _Uint(name='mothership_mmsi', nbits=30),
        ]
    ),
    _Uint(name='gps_type', nbits=4),
    _Uint(name='spare', nbits=2),
]
