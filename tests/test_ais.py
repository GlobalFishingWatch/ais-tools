import pytest
from ais_tools import ais
from ais_tools.ais import AISMessageTranscoder as AISMessage

import ais as libais
from ais import DecodeError


@pytest.mark.parametrize("body,pad,ignore", [
    ('B>cSnNP006Vuqd5aC;?Q3wVQjFLr', 0, {}),
    ('B5O3hLP00H`fAd4naG6E3wR5oP06', 0, {'cog', 'sog', 'commstate_cs_fill'}),
    ('B6:`hQ@0021M<;T=IQ:FWwR61P06', 0, {'cog', 'commstate_cs_fill'}),
    ('B39J`I0000?Dql7gCSwQ3wWQjE2b', 0, {}),
    ('B6:k??@0021FQ5SBI0q`GwpSQP06', 0, {'cog'}),
    ('H>cSnNTU7B=40058qpmjhh000004', 0, {'vendor_id', 'spare'}),
    ('H>cSnNP@4eEL544000000000000', 2, {}),
    ('I0000027FtlE01000VNJ;0`:h`0', 2, {}),
])
def test_nmea_vs_libais(body, pad, ignore):
    t = AISMessage()
    actual = t.decode_nmea(body, pad)
    expected = libais.decode(body, pad)
    assert (body, pad) == t.encode_nmea(actual)

    expected = {k: v for k, v in expected.items() if k not in ignore}
    actual = {k: v for k, v in actual.items() if k in expected}
    assert expected == actual


@pytest.mark.parametrize("body,pad,expected", [
    ('H>cSnNTU7B=40058qpmjhh000004', 0,
     {'vendor_id': 'GRMD@@E', 'vendor_id_1371_4': 'GRM', 'spare': 0, 'vendor_model': 1, 'vendor_serial': 5, 'gps_type': 1}),
])
def test_ais24_part_b(body, pad, expected):
    actual = AISMessage().decode_nmea(body, pad)
    assert expected == {k: v for k, v in actual.items() if k in expected}


def test_ais24_part_a_incorrect_pad():
    # The correct pad for this message is 2, but sometimes these are found with pad=0
    # libais will complain about the 2 extra bits at the end but we want to
    # just ignore them instead

    body = 'H>cSnNP@4eEL544000000000000'
    pad = 0
    with pytest.raises(DecodeError):
        libais.decode(body, pad)
    actual = AISMessage().decode_nmea(body, pad)
    expected = {'name': 'DAKUWAQA@@@@@@@@@@@@'}
    assert expected == {k: v for k, v in actual.items() if k in expected}


@pytest.mark.parametrize("msg", [
    ({'id': 25, 'text': 'SOME TEXT'}),
    ({'id': 25, 'text': 'SOME TEXT', 'addressed': 1, 'dest_mmsi': 123456789}),
])
def test_ais25(msg):
    t = AISMessage()
    body, pad = t.encode_nmea(msg)
    print(body, pad)
    actual = t.decode_nmea(body, pad)
    assert msg == {k: v for k, v in actual.items() if k in msg}
