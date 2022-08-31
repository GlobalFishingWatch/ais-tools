import pytest
import re

from ais_tools.nmea import join_multipart
from ais_tools.nmea import split_multipart
from ais_tools.nmea import join_multipart_stream
from ais_tools.nmea import expand_nmea
from ais_tools.ais import DecodeError


@pytest.mark.parametrize("line,expected", [
    ("\\s:rORBCOMM000,q:u,c:1509502436,T:2017-11-01 02.13.56*50\\!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*7B",
        {'tagblock_timestamp': 1509502436, 'tagblock_sentence': 1}),
    ("\\g:1-2-4372,s:rORBCOMM109,c:1426032000,T:2015-03-11 00.00.00*32"
     "\\!AIVDM,2,1,2,B,576u>F02>hOUI8AGR20tt<j104p4l62222222216H14@@Hoe0JPEDp1TQH88,0*16",
        {'tagblock_sentence': 1, 'tagblock_groupsize': 2}),
    ("\\g:2-2-4372,s:rORBCOMM109,c:1426032000,T:2015-03-11 00.00.00*31"
     "\\!AIVDM,2,2,2,B,88888888880,2*25",
        {'tagblock_sentence': 2, 'tagblock_groupsize': 2}),
    ("\\s:rORBCOMM109,c:1426032000,T:2015-03-11 00.00.00*32"
     "\\!AIVDM,2,1,2,B,576u>F02>hOUI8AGR20tt<j104p4l62222222216H14@@Hoe0JPEDp1TQH88,0*16",
        {'tagblock_sentence': 1, 'tagblock_groupsize': 2}),
    ("\\s:rORBCOMM109,c:1426032000,T:2015-03-11 00.00.00*31\\!AIVDM,2,2,2,B,88888888880,2*25",
        {'tagblock_sentence': 2, 'tagblock_groupsize': 2}),
    ('\\c:1577762601537,s:sdr-experiments,T:2019-12-30 22.23.21*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49',
        {'tagblock_station': 'sdr-experiments', 'tagblock_channel': 'A'})
])
def test_expand_nmea(line, expected):
    tagblock, body, pad = expand_nmea(line)
    assert set(expected.items()).issubset(set(tagblock.items()))


@pytest.mark.parametrize("nmea", [
    '',
    'invalid',
    '!AIVDM,NOT_AN_INT,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49',
    '!AIVDM,1,1,'
    "\\s:bad-nmea,q:u,c:1509502436,T:2017-11-01 02.13.56*50\\!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*00",
    "\\s:missing-tagblock-separator,q:u,c:1509502436,T:2017-11-01 02.13.56*50!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*00",
    "\\s:missing-tagblock-checksum,q:u,c:1509502436,T:2017-11-01 02.13.56\\!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*00",
    "\\s:missing_field_delimiter,q:u,c1509502436,T:2017-11-01 02.13.56*50\\!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*7B",
    "\\s:bad_group,q:u,c:1509502436,T:2017-11-01 02.13.56*50\\!AIVDM,BAD,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*0D",
    "\\s:missing_checksum,q:u,c:1509502436,T:2017-11-01 02.13.56\\!AIVDM,BAD,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*0D",
])
def test_expand_nmea_fail(nmea):
    with pytest.raises(DecodeError):
        tagblock, body, pad = expand_nmea(nmea)


@pytest.mark.parametrize("nmea", [
    (['!AIVDM,2,1,7,A,@*00']),
    (['!AIVDM,2,1,7,A,@*00', '!AIVDM,2,1,7,A,@*00']),
    (['\\t:1*00\\!AIVDM,2,1,7,A,@*00', '\\t:2*00\\!AIVDM,2,2,7,A,@*00'])
])
def test_join_multipart(nmea):
    print(nmea)
    line = join_multipart(nmea)
    assert line == ''.join(nmea)
    assert split_multipart(line) == nmea


def test_join_multipart_fail():
    with pytest.raises(DecodeError):
        join_multipart('AIVDM-does-not-start-with-!')


@pytest.mark.parametrize("nmea", [
    ('!AIVDM,2,1,7,A,@*6F'),
    ('!AIVDM,2,1,7,A,@*6F!AIVDM,2,1,7,A,@*6F'),
    ('\\!AIVDM,2,1,7,A,@*6F\\!AIVDM,2,1,7,A,@*6F'),
    ('\\t:1*00\\!AIVDM,2,1,7,A,@*00\\t:2*00\\!AIVDM,2,2,7,A,@*00')
])
def test_split_multipart(nmea):
    lines = split_multipart(nmea)
    assert ''.join(lines) == nmea == join_multipart(lines)


@pytest.mark.parametrize("nmea,error", [
    ('', 'no valid AIVDM message detected'),
    ('not_nmea', 'no valid AIVDM message detected'),
])
def test_split_multipart_fail(nmea, error):
    with pytest.raises(DecodeError, match=error):
        split_multipart(nmea)


def test_join_multipart_stream_singleton():
    nmea = ['!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49']
    combined = list(join_multipart_stream(nmea))
    assert len(combined) == 1
    assert combined == nmea


@pytest.mark.parametrize("nmea", [
    (['\\g:1-2-1561,s:rORBCOMM000,c:1598653784,T:2020-08-28 22.29.44*39'
      '\\!AIVDM,2,1,1,B,56:`@2h00001`dQP001`PDpMPTs7SH000000001@0000000000<000000000,0*3E',
      '\\g:2-2-1561,s:rORBCOMM000,c:1598653784,T:2020-08-28 22.29.44*3a\\!AIVDM,2,2,1,B,00000000000,2*26']),
    (['\\t:1,g:1-2-1561,s:station1*00\\!AIVDM,2,1,1,B,@,0*57',
        '\\t:2,g:2-2-1561,s:station1*00\\!AIVDM,2,2,1,B,@,0*54']),
    (['\\t:1*00\\!AIVDM,2,1,7,B,@,0*51',
      '\\t:2*00\\!AIVDM,2,2,7,B,@,0*52']),
    (['!AIVDM,2,1,7,B,@,0*51',
      '!AIVDM,2,2,7,B,@,0*52']),
])
def test_join_multipart_stream_pairs(nmea):
    combined = list(join_multipart_stream(nmea))
    assert len(combined) == 1
    assert combined == [''.join(nmea)]

    combined = list(join_multipart_stream(reversed(nmea)))
    assert len(combined) == 1
    assert combined == [''.join(nmea)]


@pytest.mark.parametrize("nmea", [
    (['!AIVDM,2,1,7,B,@,0*51',
      '!AIVDM,2,1,7,B,@,0*51',
      '!AIVDM,2,2,7,B,@,0*52']),
])
def test_join_multipart_stream_triple(nmea):
    combined = list(join_multipart_stream(nmea))
    assert len(combined) == 2
    assert combined == [nmea[0], ''.join(nmea[1:])]


@pytest.mark.parametrize("nmea", [
    (['\\g:1-2-1786,s:MAEROSPACE-C,c:1516060792*31'
      '\\!AIVDM,2,1,6,B,55R;bN02>brS<D=6220pt8hF0t4f222222222216BHGC84HC0Gm5p2j28888,0*56',
      '\\g:2-2-1786*55\\!AIVDM,2,2,6,B,88888888880,2*21']),
])
def test_join_multipart_stream_station_id_mismatch(nmea):
    combined = list(join_multipart_stream(nmea, use_station_id=True))
    assert len(combined) == 2
    assert combined == nmea

    combined = list(join_multipart_stream(nmea, use_station_id=False))
    assert len(combined) == 1
    assert combined == [''.join(nmea)]


def test_join_multipart_stream_mixed():
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

    lines = list(join_multipart_stream(nmea))
    actual = [re.findall(r'\\t:([0-9][.]?[0-9]?)', line) for line in lines]
    actual = [a if len(a) > 1 else a[0] for a in actual]
    expected = ['1', '3', ['2.1', '2.2'], '4', '6', ['5.1', '5.2'], ['7.1', '7.2'], '8.2']
    assert actual == expected


def test_join_multipart_stream_timeout():
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

    lines = list(join_multipart_stream(nmea, max_message_window=3))
    actual = [re.findall(r'\\t:([0-9][.]?[0-9]?)', line) for line in lines]
    actual = [a if len(a) > 1 else a[0] for a in actual]
    expected = ['1', '3', '4', '6', '2.1', ['7.1', '7.2'], '5.2', '8.2', '5.1', '2.2']
    assert actual == expected


def test_join_multipart_stream_fail():
    nmea = ['invalid']
    with pytest.raises(DecodeError, match='not enough fields in nmea message'):
        list(join_multipart_stream(nmea))


def test_join_multipart_stream_fail_not_fail():
    nmea = ['invalid']
    combined = list(join_multipart_stream(nmea, ignore_decode_errors=True))
    assert combined == nmea
