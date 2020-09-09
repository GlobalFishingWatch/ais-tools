from ais_tools import transcode
from ais_tools.transcode import MessageTranscoder as Message
from ais_tools.transcode import DynamicTranscoder
from ais_tools.transcode import DecodeError
from ais_tools.transcode import UintTranscoder as Uint
from ais_tools.transcode import ASCII6Transcoder as ASCII6


class AIS24Transcoder(Message):
    def __init__(self):
        super().__init__(ais24_fields)


class AIS24PartAB(Message):
    def get_fields(self, message=None):
        part_num = message.get('part_num', 0)
        if part_num == 0:
            return ais24_part_A_fields
        elif part_num == 1:
            return ais24_part_B_fields
        else:
            raise DecodeError('AIS24: unknown part number {}'.format(part_num))


class VendorID(DynamicTranscoder):
    def __init__(self):
        self.vendorid_1371_2 = Message(ais24_vendorid_ITU_R_1371_2)
        self.vendorid_1371_4 = Message(ais24_vendorid_ITU_R_1371_4)

    def encoder(self, message):
        if 'vendor_id' in message:
            return self.vendorid_1371_2
        else:
            return self.vendorid_1371_4

    def decoders(self, message):
        return [self.vendorid_1371_2, self.vendorid_1371_4]


class DimensionOrMothership(Message):
    def __init__(self):
        super().__init__()
        self.shipDimension = Message(ais24_part_B_dimension_fields)
        self.mothershipMMSI = Message(ais24_part_B_mothership_fields)

    def get_fields(self, message=None):
        mmsi = message.get('id')
        if mmsi // 10000000 == 98:
            return [self.mothershipMMSI]
        else:
            return [self.shipDimension]


# COMMON FIELDS
ais24_fields = [
    Uint(name='repeat_indicator', nbits=2),
    Uint(name='mmsi', nbits=30),
    Uint(name='part_num', nbits=2),
    AIS24PartAB()
]

# PART A
ais24_part_A_fields = [
    ASCII6(name='name', nbits=120),
]

# PART B
ais24_vendorid_ITU_R_1371_2 =[
    ASCII6(name='vendor_id', nbits=42, default='@@@@@@@'),
]

ais24_vendorid_ITU_R_1371_4 =[
    ASCII6(name='vendor_id_1371_4', nbits=18, default='@@@'),
    Uint(name='vendor_model', nbits=4),
    Uint(name='vendor_serial', nbits=20),
]

ais24_part_B_dimension_fields = [
    Uint(name='dim_a', nbits=9),
    Uint(name='dim_b', nbits=9),
    Uint(name='dim_c', nbits=6),
    Uint(name='dim_d', nbits=6),
]

ais24_part_B_mothership_fields = [
    Uint(name='mothership_mmsi', nbits=30),
]

ais24_part_B_fields = [
    Uint(name='type_and_cargo', nbits=8),
    VendorID(),
    ASCII6(name='callsign', nbits=42, default='@@@@@@@'),
    DimensionOrMothership(),
    Uint(name='gps_type', nbits=4),
    Uint(name='spare', nbits=2),
]





