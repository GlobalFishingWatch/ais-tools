from ais_tools.transcode import NmeaBits
from ais_tools.transcode import NmeaStruct as Struct
from ais_tools.transcode import UintField as Uint
from ais_tools.transcode import ASCII8toASCII6_decode_tree
from ais_tools.transcode import ASCII8toASCII6_bits
from bitarray import bitarray


# Using this coding  http://www.e-navigation.nl/content/text-using-6-bit-ascii-1

def ais25_decode(body, pad):
    bits = NmeaBits.from_nmea(body, pad)
    message = bits.unpack(ais25_fields)

    if message['addressed']:
        message.update(bits.unpack(ais25_destination_fields))

    message.update(bits.unpack(ais25_dac_fi_fields))

    text_bits = bits.bits[bits.offset:]
    message['text'] = ''.join(text_bits.iterdecode(ASCII8toASCII6_decode_tree))

    return message


def ais25_encode(message):
    text = message.get('text', '')
    length = ais25_fields.nbits + ais25_dac_fi_fields.nbits + len(text) * 6
    addressed = message.get('addressed', 0)
    if addressed:
        length += ais25_destination_fields.nbits

    bits = NmeaBits(length)
    bits.pack(ais25_fields, message)

    if message.get('addressed', 0):
        bits.pack(ais25_destination_fields, message)

    bits.pack(ais25_dac_fi_fields, message)

    text_bits = bitarray()
    text_bits.encode(ASCII8toASCII6_bits, text)
    bits.bits[bits.offset:bits.length] = text_bits

    return bits.to_nmea()


ais25_fields = Struct(
    Uint(name='id', nbits=6),
    Uint(name='repeat_indicator', nbits=2, default=0),
    Uint(name='mmsi', nbits=30),
    Uint(name='addressed', nbits=1, default=0),
    Uint(name='use_app_id', nbits=1, default=0),
)

ais25_destination_fields = Struct(
    Uint(name='dest_mmsi', nbits=30),
    Uint(name='spare', nbits=2, default=0),
)

ais25_dac_fi_fields = Struct(
    Uint(name='dac', nbits=10, default=1),
    Uint(name='fi', nbits=6, default=0),
    Uint(name='text_seq', nbits=11, default=0),
)
