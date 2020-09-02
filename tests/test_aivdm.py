import pytest
import re

from ais_tools import aivdm


@pytest.mark.parametrize("line,timestamp", [
    ("\\s:rORBCOMM000,q:u,c:1509502436,T:2017-11-01 02.13.56*50\\!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*7B",
     1509502436),
    (
    "\\s:missing_tagblock_delimeter,q:u,c:1509502436,T:2017-11-01 02.13.56*50!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*7B",
    1509502436),
    (
    "\\s:missing_field_delimiter,q:u,c1509502436,T:2017-11-01 02.13.56*50!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*7B",
    0),
    (
    "\\g:1-2-9907,s:rORBCOMM00,c:1327423135*6d\\!AIVDM,2,1,7,B,56:ToV0000008Q@S400nuJ0`Tr1UD4r1<PDpN3T:000004Hl0AVR5B0B@000,0*10",
    1327423135),
])
def test_safe_tagblock_timestamp(line, timestamp):
    assert aivdm.safe_tagblock_timestamp(line) == timestamp


# def test_ais_line_parts(line, expected):
#     tagblock, nmea = decode.ais_line_parts(line)
#     assert set(expected.items()).issubset(set(tagblock.items()))

@pytest.mark.parametrize("line,expected", [
    ("\\s:rORBCOMM000,q:u,c:1509502436,T:2017-11-01 02.13.56*50\\!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*7B",
        {'tagblock_timestamp': 1509502436, 'tagblock_sentence': 1}),
    ("\\g:1-2-4372,s:rORBCOMM109,c:1426032000,T:2015-03-11 00.00.00*32\\!AIVDM,2,1,2,B,576u>F02>hOUI8AGR20tt<j104p4l62222222216H14@@Hoe0JPEDp1TQH88,0*16",
        {'tagblock_sentence': 1, 'tagblock_groupsize': 2}),
    ("\\g:2-2-4372,s:rORBCOMM109,c:1426032000,T:2015-03-11 00.00.00*31\\!AIVDM,2,2,2,B,88888888880,2*25",
        {'tagblock_sentence': 2, 'tagblock_groupsize': 2}),
    ("\\s:rORBCOMM109,c:1426032000,T:2015-03-11 00.00.00*32\\!AIVDM,2,1,2,B,576u>F02>hOUI8AGR20tt<j104p4l62222222216H14@@Hoe0JPEDp1TQH88,0*16",
        {'tagblock_sentence': 1, 'tagblock_groupsize': 2}),
    ("\\s:rORBCOMM109,c:1426032000,T:2015-03-11 00.00.00*31\\!AIVDM,2,2,2,B,88888888880,2*25",
        {'tagblock_sentence': 2, 'tagblock_groupsize': 2}),
    ('\\c:1577762601537,s:sdr-experiments,T:2019-12-30 22.23.21*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49',
        {'tagblock_station': 'sdr-experiments', 'tagblock_channel': 'A'})
])
def test_expand_nmea(line, expected):
    tagblock, body, pad = aivdm.expand_nmea(line)
    assert set(expected.items()).issubset(set(tagblock.items()))


@pytest.mark.parametrize("nmea", [
    '!AIVDM,NOT_AN_INT,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49',
    '!AIVDM,1,1,'
    "\\s:bad-nmea,q:u,c:1509502436,T:2017-11-01 02.13.56*50\\!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*00",
    "\\s:missing-tagblock-separator,q:u,c:1509502436,T:2017-11-01 02.13.56*50!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*00",
    "\\s:missing-tagblock-checksum,q:u,c:1509502436,T:2017-11-01 02.13.56\\!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*00",
    "\\s:missing_field_delimiter,q:u,c1509502436,T:2017-11-01 02.13.56*50\\!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*7B",
    "\\s:bad_group,q:u,c:1509502436,T:2017-11-01 02.13.56*50\\!AIVDM,BAD,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*0D",
])
def test_expand_nmea_fail(nmea):
    with pytest.raises(aivdm.libais.DecodeError):
        tagblock, body, pad = aivdm.expand_nmea(nmea)


@pytest.mark.parametrize("nmea,expected", [
    ('!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49', {"mmsi": 367596940}),
    ('\\c:1577762601537,s:sdr-experiments,T:2019-12-30 22.23.21*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49',
     {"tagblock_station": "sdr-experiments"}),
])
def test_decode_message(nmea, expected):
    actual = aivdm.decode_message(nmea)
    actual_subset = {k: v for k, v in actual.items() if k in expected}
    assert actual_subset == expected


@pytest.mark.parametrize("nmea", [
    "!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,1*7B",
    '!AIVDM,1,1,,A,83am8S@j<d8dtfMEuj9loFOM6@00,0*69',
])
def test_decode_message_fail(nmea):
    with pytest.raises(aivdm.libais.DecodeError):
        aivdm.decode_message(nmea)


def test_decode_stream():
    nmea = ['\\c:1577762601537,s:sdr-experiments,T:2019-12-30 22.23.21*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49']
    assert len(list(aivdm.decode_stream(nmea))) == len(nmea)


# test for issue #1 Workaround for type 24 with bad bitcount
def test_bad_bitcount_type_24():
    nmea = '!AIVDM,1,1,,B,H>cSnNP@4eEL544000000000000,0*3E'
    actual = aivdm.decode_message(nmea)
    assert actual.get('error') is None
    assert actual.get('name') == 'DAKUWAQA@@@@@@@@@@@@'


@pytest.mark.parametrize("nmea", [
    (['!AIVDM,2,1,7,A,@*00']),
    (['!AIVDM,2,1,7,A,@*00', '!AIVDM,2,1,7,A,@*00']),
    (['\\t:1*00\\!AIVDM,2,1,7,A,@*00', '\\t:2*00\\!AIVDM,2,2,7,A,@*00'])
])
def test_join_multipart(nmea):
    print(nmea)
    line = aivdm.join_multipart(nmea)
    print (line)
    assert line == ''.join(nmea)
    assert aivdm.split_multipart(line) == nmea


def test_join_multipart_fail():
    with pytest.raises(ValueError):
        line = aivdm.join_multipart('AIVDM-does-not-start-with-!')


@pytest.mark.parametrize("nmea", [
    ('!AIVDM,2,1,7,A,@*6F'),
    ('!AIVDM,2,1,7,A,@*6F!AIVDM,2,1,7,A,@*6F'),
    ('\\t:1*00\\!AIVDM,2,1,7,A,@*00\\t:2*00\\!AIVDM,2,2,7,A,@*00')
])
def test_split_multipart(nmea):
    lines = aivdm.split_multipart(nmea)
    assert ''.join(lines) == nmea == aivdm.join_multipart(lines)


def test_multipart_singleton():
    nmea = ['!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49']
    combined = list(aivdm.join_multipart_stream(nmea))
    assert len(combined) == 1
    assert combined == nmea


@pytest.mark.parametrize("nmea", [
    (['\\g:1-2-1561,s:rORBCOMM000,c:1598653784,T:2020-08-28 22.29.44*39\\!AIVDM,2,1,1,B,56:`@2h00001`dQP001`PDpMPTs7SH000000001@0000000000<000000000,0*3E',
        '\\g:2-2-1561,s:rORBCOMM000,c:1598653784,T:2020-08-28 22.29.44*3a\\!AIVDM,2,2,1,B,00000000000,2*26']),
    (['\\t:1,g:1-2-1561,s:station1*00\\!AIVDM,2,1,1,B,@,0*57',
        '\\t:2,g:2-2-1561,s:station1*00\\!AIVDM,2,2,1,B,@,0*54']),
    (['\\t:1*00\\!AIVDM,2,1,7,B,@,0*51',
      '\\t:2*00\\!AIVDM,2,2,7,B,@,0*52']),
    (['!AIVDM,2,1,7,B,@,0*51',
      '!AIVDM,2,2,7,B,@,0*52']),
])
def test_multipart_pairs(nmea):
    combined = list(aivdm.join_multipart_stream(nmea))
    assert len(combined) == 1
    assert combined == [''.join(nmea)]

    combined = list(aivdm.join_multipart_stream(reversed(nmea)))
    assert len(combined) == 1
    assert combined == [''.join(nmea)]


def test_multipart_mixed():
    nmea = [
        '\\t:1,s:station1*00\\!AIVDM,1,1,1,A,@,0*57',
        '\\t:2.1,g:1-2-001,s:station1*00\\!AIVDM,2,1,1,B,@,0*57',
        '\\t:3,s:station1*00\\!AIVDM,1,1,1,A,@,0*57',
        '\\t:2.2,g:2-2-001,s:station1*00\\!AIVDM,2,2,1,B,@,0*54',
        '\\t:4,s:station1*00\\!AIVDM,1,1,1,A,@,0*57',
        '\\t:5.2*00\\!AIVDM,2,2,5,B,@,0*50',
        '\\t:6,s:station1*00\\!AIVDM,1,1,1,A,@,0*57',
        '\\t:8.2*00\\!AIVDM,2,2,8,A,@,0*5E',
        '\\t:7.1*00\\!AIVDM,2,1,7,B,@,0*51',
        '\\t:5.1*00\\!AIVDM,2,1,5,B,@,0*53',
        '\\t:7.2*00\\!AIVDM,2,2,7,B,@,0*52'
    ]

    lines = list(aivdm.join_multipart_stream(nmea))
    actual = [re.findall(r'\\t:([0-9][.]?[0-9]?)', line) for line in lines]
    actual = [a if len(a) > 1 else a[0] for a in actual]
    print(actual)
    expected = ['1', '3', ['2.1', '2.2'], '4', '6', ['5.1', '5.2'], ['7.1', '7.2'], '8.2']
    assert actual == expected


def test_multipart_timeout():
    nmea = [
        '\\t:1,s:station1*51\\!AIVDM,1,1,1,A,@,0*57',
        '\\t:2.1,g:1-2-001,s:station1*00\\!AIVDM,2,1,1,B,@,0*57',
        '\\t:3,s:station1*00\\!AIVDM,1,1,1,A,@,0*57',
        '\\t:4,s:station1*00\\!AIVDM,1,1,1,A,@,0*57',
        '\\t:5.2*00\\!AIVDM,2,2,5,B,@,0*50',
        '\\t:6,s:station1*00\\!AIVDM,1,1,1,A,@,0*57',
        '\\t:8.2*00\\!AIVDM,2,2,8,A,@,0*5E',
        '\\t:7.1*00\\!AIVDM,2,1,7,B,@,0*51',
        '\\t:7.2*00\\!AIVDM,2,2,7,B,@,0*52',
        '\\t:5.1*00\\!AIVDM,2,1,5,B,@,0*53',
        '\\t:2.2,g:2-2-001,s:station1*00\\!AIVDM,2,2,1,B,@,0*54',
    ]

    lines = list(aivdm.join_multipart_stream(nmea, max_message_window=3))
    actual = [re.findall(r'\\t:([0-9][.]?[0-9]?)', line) for line in lines]
    actual = [a if len(a) > 1 else a[0] for a in actual]
    expected = ['1', '3', '4', '6', '2.1', ['7.1', '7.2'], '5.2', '8.2', '5.1', '2.2']
    assert actual == expected



