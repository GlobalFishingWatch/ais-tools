import pytest
import cbitstruct as bitstruct
from ais_tools import transcode
from ais_tools.transcode import NmeaBits
from ais_tools.transcode import NmeaStruct
from ais_tools.transcode import EncodedField
from ais_tools.transcode import UintField as Uint
from ais_tools.transcode import Uint10Field as Uint10
from ais_tools.transcode import LatLonField as LatLon
from ais_tools.transcode import BoolField as Bool
from ais_tools.transcode import BitField as Bit
from ais_tools.transcode import HexField as Hex
from ais_tools.transcode import ASCII6Field as ASCII6


def test_AIS6():
    assert transcode.AIS6toASCII8[12] == '<'
    for i, c in enumerate(transcode.AIS6toASCII8):
        assert transcode.ASCII8toAIS6[c] == i


def test_ASCII6():
    assert transcode.ASCII6toASCII8[12] == 'L'
    for i, c in enumerate(transcode.ASCII6toASCII8):
        assert transcode.ASCII8toASCII6[c] == i


@pytest.mark.parametrize("body,pad", [
    ('', 0),
    ('0', 0),
    ('0', 2),
    ('w', 0),
    ('w0', 5),
])
def test_nmea_to_bits(body, pad):
    bits = transcode.nmea_to_bits(body, pad)
    assert len(bits) == len(body) * 6 - pad
    decoded = transcode.bits_to_nmea(bits)
    assert decoded == (body, pad)


@pytest.mark.parametrize("body,pad", [
    ('ABC', 0),
    ('@', 2),
    ('', 0),
    (''.join(transcode.AIS6toASCII8), 0)
])
def test_NmeaBits_from_nmea(body, pad):
    assert NmeaBits.from_nmea(body, pad).to_nmea() == (body, pad)


def test_NmeaStruct():
    s = NmeaStruct(
        Uint(name='A', nbits=6, default=1),
        Uint10(name='B', nbits=8),
        LatLon(name='C', nbits=20),
        Bit(name='D', nbits=12)
    )
    assert s.names == ['A', 'B', 'C', 'D']
    assert s.nbits == 46
    assert s.format_str == 'u6u8s20r12'
    assert bitstruct.calcsize(s.format_str) == s.nbits
    assert s.defaults == {'A': 1}


def test_unpack_NmeaStruct():
    bits = NmeaBits.from_nmea('123', 0)
    s = NmeaStruct(
        Uint('A', 6),
        Uint10('B', 6),
        Uint('C', 6)
    )
    message = bits.unpack(s)
    assert message == {'A': 1, 'B': 0.2, 'C': 3}
    assert bits.offset == s.nbits


def test_pack_NmeaStruct():
    bits = NmeaBits(18)
    s = NmeaStruct(
        Uint(name='A', nbits=6),
        Uint10(name='B', nbits=6),
        Uint(name='C', nbits=6, default=3)
    )
    message = {'A': 1, 'B': 0.2}
    bits.pack(s, message)
    assert bits.offset == s.nbits
    assert bits.to_nmea() == ('123', 0)


@pytest.mark.parametrize("field_type,value,nbits,format_str", [
    (Uint, 1, 6, 'u6'),
    (Uint10, 1.2, 6, 'u6'),
    (LatLon, -123.456, 28, 's28'),
    (Bool, True, 1, 'b1'),
    (Bit, '010101', 6, 'r6'),
    (Hex, 'abc', 12, 'r12'),
    (ASCII6, 'TEST', 24, 'r24'),
])
def test_fields(field_type, value, nbits, format_str):
    field = field_type('name', nbits)
    assert field.format_str == format_str
    if isinstance(field, EncodedField):
        assert field.decode(field.encode(value)) == value
