import pytest
import re

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


def test_multipart_singleton():
    nmea = ['!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49']
    combined = list(aivdm.combine_multipart_messages(nmea))
    assert len(combined) == 1
    assert combined == nmea

@pytest.mark.parametrize("nmea", [
    (['\\g:1-2-1561,s:rORBCOMM000,c:1598653784,T:2020-08-28 22.29.44*39\\!AIVDM,2,1,1,B,56:`@2h00001`dQP001`PDpMPTs7SH000000001@0000000000<000000000,0*3E',
        '\\g:2-2-1561,s:rORBCOMM000,c:1598653784,T:2020-08-28 22.29.44*3a\\!AIVDM,2,2,1,B,00000000000,2*26']),
    (['\\t:1,g:1-2-1561,s:station1*00\\!AIVDM,2,1,1,B,@*00',
        '\\t:2,g:2-2-1561,s:station1*00\\!AIVDM,2,2,1,B,@*00']),
    (['\\t:1*00\\!AIVDM,2,1,7,A,@*00',
      '\\t:2*00\\!AIVDM,2,2,7,A,@*00']),
    (['!AIVDM,2,1,7,A,@*00',
      '!AIVDM,2,2,7,A,@*00']),
])
def test_multipart_pairs(nmea):
    combined = list(aivdm.combine_multipart_messages(nmea))
    assert len(combined) == 1
    assert combined == [''.join(nmea)]

    combined = list(aivdm.combine_multipart_messages(reversed(nmea)))
    assert len(combined) == 1
    assert combined == [''.join(nmea)]


def test_multipart_mixed():
    nmea = [
        '\\t:1,s:station1*00\\!AIVDM,1,1,1,A,@*00',
        '\\t:2.1,g:1-2-001,s:station1*00\\!AIVDM,2,1,1,B,@*00',
        '\\t:3,s:station1*00\\!AIVDM,1,1,1,A,@*00',
        '\\t:2.2,g:2-2-001,s:station1*00\\!AIVDM,2,2,1,B,@*00',
        '\\t:4,s:station1*00\\!AIVDM,1,1,1,A,@*00',
        '\\t:5.2*00\\!AIVDM,2,2,5,B,@*00',
        '\\t:6,s:station1*00\\!AIVDM,1,1,1,A,@*00',
        '\\t:8.2*00\\!AIVDM,2,2,8,A,@*00',
        '\\t:7.1*00\\!AIVDM,2,1,7,B,@*00',
        '\\t:5.1*00\\!AIVDM,2,1,5,B,@*00',
        '\\t:7.2*00\\!AIVDM,2,2,7,B,@*00'
    ]

    lines = list(aivdm.combine_multipart_messages(nmea))
    actual = [re.findall(r'\\t:([0-9][.]?[0-9]?)', line) for line in lines]
    actual = [a if len(a) > 1 else a[0] for a in actual]
    print(actual)
    expected = ['1', '3', ['2.1', '2.2'], '4', '6', ['5.1', '5.2'], ['7.1', '7.2'], '8.2']
    assert actual == expected


