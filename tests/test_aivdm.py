import pytest

from ais_tools import aivdm
from ais_tools.aivdm import AIVDM
from ais_tools.message import Message


@pytest.mark.parametrize("nmea,expected", [
    ('!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49', {"mmsi": 367596940}),
    ('\\c:1577762601537,s:sdr-experiments,T:2019-12-30 22.23.21*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49',
     {"tagblock_station": "sdr-experiments"}),
    ('!AIVDM,2,1,7,A,<M000000000000000000GcMvmEEEOPB6??uR0001np`R0;gbpaR@gP7GbSeH,0*63!AIVDM,2,2,7,A,OeEEEGp4Qf<,2*74',
     {"mmsi": 872415232}),
    ('!AIVDM,1,1,,A,83am8S@j<d8dtfMEuj9loFOM6@00,0*69', {'id': 8}),

])
def test_decode(nmea, expected):
    decoder = AIVDM()
    actual = decoder.decode(nmea)
    actual_subset = {k: v for k, v in actual.items() if k in expected}
    assert actual_subset == expected


@pytest.mark.parametrize("nmea,error", [
    ('!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,1*7B', 'Invalid checksum'),
    ('!AIVDM,2,1,1,B,@,0*57', 'Expected 2 message parts to decode but found 1'),
    ('!', 'No valid AIVDM found in'),
    ('!AIVDM,1,1,,A,B99999,0*5D', 'AISTOOLS ERR: Not enough bits to decode.  Need at least 149 bits, got only 36')
])
def test_decode_fail(nmea, error):
    decoder = AIVDM()
    with pytest.raises(aivdm.libais.DecodeError, match=error):
        decoder.decode(nmea)


# test for issue #1 Workaround for type 24 with bad bitcount
def test_bad_bitcount_type_24():
    decoder = AIVDM()
    nmea = '!AIVDM,1,1,,B,H>cSnNP@4eEL544000000000000,0*3E'
    actual = decoder.decode(nmea)
    assert actual.get('error') is None
    assert actual.get('name') == 'DAKUWAQA@@@@@@@@@@@@'


def test_encode():
    encoder = AIVDM()
    msg = Message(
        id=25, mmsi=123456789
    )
    expected = Message('!AIVDM,1,1,,A,I1mg=5@0@000,5*59')
    assert expected == encoder.encode(msg)


@pytest.mark.parametrize("message,error", [
    ({'id': 24, 'mmsi': 123456789, 'part_num': 2}, 'AIS24: unknown part number 2'),
])
def test_encode_fail(message, error):
    encoder = AIVDM()
    with pytest.raises(aivdm.libais.DecodeError, match=error):
        encoder.encode(message)


def test_safe_decode():
    decoder = AIVDM()
    nmea = '\\s:66,c:1662392995*32\\!AIVDM,1,1,,B,6NlUC7@00000>d`w0000@00,2*6F'
    msg = decoder.safe_decode(nmea=nmea, best_effort=True)
    assert msg['error'] == 'AISTOOLS ERR: None  LIBAIS ERR: Ais6: DAC:FI not known.  6:235:10 AIS_UNINITIALIZED'
    assert msg['tagblock_timestamp'] == 1662392995
