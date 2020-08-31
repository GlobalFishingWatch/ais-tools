import unittest
import pytest

from ais_tools import aivdm


NMEA = [
    '\\c:1577762601537,s:sdr-experiments,T:2019-12-30 22.23.21*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49'
]


@pytest.mark.parametrize("nmea,expected", [
    ('!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49', {"mmsi": 367596940}),
    ('\\c:1577762601537,s:sdr-experiments,T:2019-12-30 22.23.21*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49',
     {"tagblock_station": "sdr-experiments"}),
])
def test_decode_message(nmea, expected):
    actual = aivdm.decode_message(nmea)
    actual_subset = {k: v for k, v in actual.items() if k in expected}
    assert actual_subset == expected


def test_decode_stream():
    assert len(list(aivdm.decode_stream(NMEA))) == len(NMEA)


# test for issue #1 Workaround for type 24 with bad bitcount
def test_bad_bitcount_type_24():
    nmea = '!AIVDM,1,1,,B,H>cSnNP@4eEL544000000000000,0*3E'
    actual = aivdm.decode_message(nmea)
    assert actual.get('error') is None
    assert actual.get('name') == 'DAKUWAQA@@@@@@@@@@@@'
