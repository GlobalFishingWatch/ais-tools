from ais_tools.transcode import MessageTranscoder as Message
from ais_tools.transcode import DecodeError
from ais_tools.transcode import UintTranscoder as Uint
from ais_tools.transcode import ASCII6Transcoder as ASCII6


class AIS24Transcoder(Message):

    def part_AB_fields(self, part_num):
        if part_num == 0:
            return ais24_part_A_fields
        elif part_num == 1:
            return ais24_part_B_fields
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
        mmsi = message.get('id')
        if mmsi // 10000000 == 98:
            return self.mothership_fields
        else:
            return self.dim_fields


# PART A
ais24_part_A_fields = [
    Uint(name='id', nbits=6, default=0),
    Uint(name='repeat_indicator', nbits=2),
    Uint(name='mmsi', nbits=30),
    Uint(name='part_num', nbits=2),
    ASCII6(name='name', nbits=120),
]


ais24_part_B_fields = [
    Uint(name='id', nbits=6, default=0),
    Uint(name='repeat_indicator', nbits=2),
    Uint(name='mmsi', nbits=30),
    Uint(name='part_num', nbits=2),
    Uint(name='type_and_cargo', nbits=8),
    VendorID(
        [
            ASCII6(name='vendor_id', nbits=42, default='@@@@@@@'),
        ],
        [
            ASCII6(name='vendor_id_1371_4', nbits=18, default='@@@'),
            Uint(name='vendor_model', nbits=4),
            Uint(name='vendor_serial', nbits=20),
        ],
    ),
    ASCII6(name='callsign', nbits=42, default='@@@@@@@'),
    DimensionOrMothership(
        [
            Uint(name='dim_a', nbits=9),
            Uint(name='dim_b', nbits=9),
            Uint(name='dim_c', nbits=6),
            Uint(name='dim_d', nbits=6),
        ],
        [
            Uint(name='mothership_mmsi', nbits=30),
        ]
    ),
    Uint(name='gps_type', nbits=4),
    Uint(name='spare', nbits=2),
]
