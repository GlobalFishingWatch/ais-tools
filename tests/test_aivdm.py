import pytest
import re

from ais_tools import aivdm
from ais_tools.aivdm import AIVDM


@pytest.mark.parametrize("nmea,expected", [
    ('!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49', {"mmsi": 367596940}),
    ('\\c:1577762601537,s:sdr-experiments,T:2019-12-30 22.23.21*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49',
     {"tagblock_station": "sdr-experiments"}),
])
def test_decode(nmea, expected):
    decoder = AIVDM()
    actual = decoder.decode(nmea)
    actual_subset = {k: v for k, v in actual.items() if k in expected}
    assert actual_subset == expected


@pytest.mark.parametrize("nmea,error", [
    ('!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,1*7B', 'Invalid checksum'),
    ('!AIVDM,1,1,,A,83am8S@j<d8dtfMEuj9loFOM6@00,0*69', 'Type check failed in field spare2.*'),
     ('!AIVDM,2,1,1,B,@,0*57', 'Expected 2 message parts to decode but found 1'),
])
def test_decode_fail(nmea, error):
    decoder = AIVDM()
    with pytest.raises(aivdm.libais.DecodeError, match=error):
        decoder.decode(nmea)


def test_decode_stream():
    decoder = AIVDM()
    nmea = ['\\c:1577762601537,s:sdr-experiments,T:2019-12-30 22.23.21*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49']
    assert len(list(decoder.decode_stream(nmea))) == len(nmea)


# test for issue #1 Workaround for type 24 with bad bitcount
def test_bad_bitcount_type_24():
    decoder = AIVDM()
    nmea = '!AIVDM,1,1,,B,H>cSnNP@4eEL544000000000000,0*3E'
    actual = decoder.decode(nmea)
    assert actual.get('error') is None
    assert actual.get('name') == 'DAKUWAQA@@@@@@@@@@@@'


