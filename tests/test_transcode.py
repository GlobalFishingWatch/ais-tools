import pytest
from ais_tools import transcode


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


@pytest.mark.parametrize("value,cls,nbits", [
    ('0101', transcode.BitsTranscoder, 4),
    (-7, transcode.IntTranscoder, 4),
    (3, transcode.UintTranscoder, 4),
    ('ABCD', transcode.ASCII6Transcoder, 24),
    (234.5, transcode.Uint10Transcoder, 12),
    (45.6789, transcode.LatLonTranscoder, 27),
    (-123.45678, transcode.LatLonTranscoder, 28),
])
def test_transcoder_roundtrip(value, cls, nbits):
    msg = {'a': value}
    t = cls(name='a', nbits=nbits)
    encoded = t.encode(msg)
    assert len(encoded) == nbits
    decoded = t.decode(bits=encoded)
    assert decoded == msg


def test_message_transcoder():
    msg = {'a': 1, 'b': 12.34, 'c': 'ABC'}
    fields = [
        transcode.UintTranscoder(name='a', nbits=8),
        transcode.LatLonTranscoder(name='b', nbits=27),
        transcode.ASCII6Transcoder(name='c', nbits=18),
    ]
    t = transcode.MessageTranscoder(fields=fields)
    decoded = t.decode(t.encode(msg))
    assert decoded == msg


@pytest.mark.parametrize("value,nbits,expected", [
    ('1', 12, '1@'),
    ('12', 12, '12'),
    ('123', 12, '12'),
])
def test_ascii6(value, nbits, expected):
    t = transcode.ASCII6Transcoder(name='a', nbits=nbits)
    msg = {'a': value}
    actual = t.decode(t.encode(msg))
    assert actual['a'] == expected


@pytest.mark.parametrize("value,expected", [
    ('1', '1'),
    ('12', '12'),
    ('123', '123'),
])
def test_var_ascii6(value, expected):
    t = transcode.VariableLengthASCII6Transcoder(name='a')
    msg = {'a': value}
    actual = t.decode(t.encode(msg))
    assert actual['a'] == expected
