from ais_tools.transcode import NmeaBits
from ais_tools.transcode import NmeaStruct as Struct
from ais_tools.transcode import UintField as Uint
from ais_tools.transcode import HexField as Hex
from bitarray.util import hex2ba
from bitarray.util import ba2hex


def ais8_decode(body, pad):
    bits = NmeaBits.from_nmea(body, pad)
    message = bits.unpack(ais8_fields)

    data_bits = bits.bits[bits.offset:]
    if len(data_bits) % 4 != 0:
        # assume that the pad value was wrong and just ignore the extra bits at the end
        new_len = (len(data_bits) // 4) * 4
        data_bits = data_bits[:new_len]

    message['application_data'] = ba2hex(data_bits)

    return message


def ais8_encode(message):
    bits = NmeaBits(ais8_fields.nbits + len(message['application_data']) * 4)
    bits.pack(ais8_fields, message)

    data_bits = hex2ba(message['application_data'])
    bits.bits[bits.offset:bits.length] = data_bits

    return bits.to_nmea()


ais8_fields = Struct(
    Uint(name='id', nbits=6, default=8),
    Uint(name='repeat_indicator', nbits=2),
    Uint(name='mmsi', nbits=30),
    Uint(name='spare', nbits=2, default=0),
    Hex(name='application_id', nbits=16),
)
