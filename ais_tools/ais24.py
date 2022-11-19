from ais_tools.transcode import DecodeError
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

        message.update(bits.unpack_from(vendorid_1371_4, offset=48))

        if message['mmsi'] // 10000000 == 98:
            message.update(bits.unpack_from(mothership_fields, offset=132))
    else:
        raise DecodeError(f'AIS24: unknown part number {part_num}')

    return message


def ais24_encode(message):
    part_num = message.get('part_num', 0)
    if part_num == 0:
        nbits = 160
    elif part_num == 1:
        nbits = 168
    else:
        raise DecodeError(f'AIS24: unknown part number {part_num}')

    bits = NmeaBits(nbits)
    bits.pack(ais24_fields, message)
    if part_num == 0:
        name = message.get('name', '')
        name_fields = {
            'name_1': name[:10],
            'name_2': name[10:],
        }
        bits.pack(ais24_part_A_fields, name_fields)
    else:
        bits.pack(ais24_part_B_fields, message)

        if 'vendor_id_1371_4' in message:
            bits.pack_into(vendorid_1371_4, offset=48, message=message)

        if 'mothership_mmsi' in message:
            bits.pack_into(mothership_fields, offset=132, message=message)

    return bits.to_nmea()


ais24_fields = Struct(
    Uint(name='id', nbits=6, default=0),
    Uint(name='repeat_indicator', nbits=2, default=0),
    Uint(name='mmsi', nbits=30),
    Uint(name='part_num', nbits=2, default=0)
)

ais24_part_A_fields = Struct(
    ASCII6(name='name_1', nbits=60),
    ASCII6(name='name_2', nbits=60)
)

ais24_part_B_fields = Struct(
    Uint(name='type_and_cargo', nbits=8, default=0),
    ASCII6(name='vendor_id', nbits=42, default='@@@@@@@'),
    ASCII6(name='callsign', nbits=42, default='@@@@@@@'),
    Uint(name='dim_a', nbits=9, default=0),
    Uint(name='dim_b', nbits=9, default=0),
    Uint(name='dim_c', nbits=6, default=0),
    Uint(name='dim_d', nbits=6, default=0),
    Uint(name='fix_type', nbits=4, default=0),
    Uint(name='spare', nbits=2, default=0)
)

vendorid_1371_4 = Struct(
    ASCII6(name='vendor_id_1371_4', nbits=18, default='@@@'),
    Uint(name='vendor_model', nbits=4, default=0),
    Uint(name='vendor_serial', nbits=20, default=0),

)

mothership_fields = Struct(
    Uint(name='mothership_mmsi', nbits=30),
)
