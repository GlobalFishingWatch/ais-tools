from ais_tools.transcode import UintTranscoder as _Uint
from ais_tools.transcode import HexTranscoder as _Hex
from ais_tools.transcode import VariableLengthHexTranscoder as _VarHex

from ais_tools.transcode import NmeaBits
from ais_tools.transcode import NmeaStruct as Struct
from ais_tools.transcode import UintField as Uint
from ais_tools.transcode import HexField as Hex
from bitarray import bitarray
from bitarray.util import hex2ba
from bitarray.util import ba2hex


def ais8_decode(body, pad):
    bits = NmeaBits.from_nmea(body, pad)
    message = bits.unpack(ais8_fields)

    message['application_data'] = ba2hex(bits.bits[bits.offset:])

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


_ais8_fields = [
    _Uint(name='id', nbits=6, default=0),
    _Uint(name='repeat_indicator', nbits=2),
    _Uint(name='mmsi', nbits=30),
    _Uint(name='spare', nbits=2),
    _Hex(name='application_id', nbits=16),
    _VarHex(name='application_data')
]
