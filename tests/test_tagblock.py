import pytest

from ais_tools import tagblock
from ais_tools.tagblock import DecodeError


@pytest.mark.parametrize("line,expected", [
    ("\\s:rORBCOMM000,q:u,c:1509502436,T:2017-11-01 02.13.56*50\\!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*7B",
     1509502436),
    ("\\s:missing_tagblock_delimeter,q:u,c:1509502436,T:2017-11-01 02.13.56*50!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*7B",
     1509502436),
    ("\\s:missing_field_delimiter,q:u,c1509502436,T:2017-11-01 02.13.56*50!AIVDM,1,1,,A,13`el0gP000H=3JN9jb>4?wb0>`<,0*7B",
     0),
    ("\\g:1-2-9907,s:rORBCOMM00,c:1327423135*6d"
     "\\!AIVDM,2,1,7,B,56:ToV0000008Q@S400nuJ0`Tr1UD4r1<PDpN3T:000004Hl0AVR5B0B@000,0*10",
     1327423135),
    ("\\c:invalid*6d"
     "\\!AIVDM,2,1,7,B,56:ToV0000008Q@S400nuJ0`Tr1UD4r1<PDpN3T:000004Hl0AVR5B0B@000,0*10",
     0),
])
def test_safe_tagblock_timestamp(line, expected):
    assert tagblock.safe_tagblock_timestamp(line) == expected


@pytest.mark.parametrize("station,timestamp,add_tagblock_t,expected", [
    ('sta', 1, None, 'c:1000,s:sta*5B'),
    ('sta', 1, True, 'c:1000,s:sta,T:1970-01-01 00.00.01*37'),
])
def test_create_tagblock(station, timestamp, add_tagblock_t, expected):
    assert expected == tagblock.create_tagblock(station, timestamp, add_tagblock_t)


@pytest.mark.parametrize("nmea,expected", [
    ("!AIVDM", ('', '!AIVDM')),
    ("\\!AIVDM", ('', '\\!AIVDM')),
    ("\\c:1000,s:sta*5B\\!AIVDM", ('c:1000,s:sta*5B', '!AIVDM')),
    ("NOT A MESSAGE", ('', 'NOT A MESSAGE')),
])
def test_split_tagblock(nmea, expected):
    assert expected == tagblock.split_tagblock(nmea)


@pytest.mark.parametrize("t,nmea,expected", [
    ("", "", ""),
    ('', "!AIVDM", '!AIVDM'),
    ('c:1000,s:sta*5B', '!AIVDM', "\\c:1000,s:sta*5B\\!AIVDM"),
    ('\\c:1000,s:sta*5B', '!AIVDM', "\\c:1000,s:sta*5B\\!AIVDM"),
])
def test_join_tagblock(t, nmea, expected):
    assert expected == tagblock.join_tagblock(t, nmea)


@pytest.mark.parametrize("t,nmea,overwrite,expected", [
    ("", "", None, ""),
    ('c:1000,s:new*5A', '\\c:1000,s:old*5A\\!AIVDM', True, "\\c:1000,s:new*5A\\!AIVDM"),
    ('c:1000,s:new*5A', '\\c:1000,s:old*5A\\!AIVDM', False, "\\c:1000,s:old*5A\\!AIVDM"),
])
def test_add_tagblock(t, nmea, overwrite, expected):
    assert expected == tagblock.add_tagblock(t, nmea, overwrite)


@pytest.mark.parametrize("fields,expected", [
    ({}, '*00'),
    ({'z': 123}, 'z:123*70'),
    ({'tagblock_relative_time': 123}, 'r:123*78'),
    ({'tagblock_timestamp': 123456789}, 'c:123456789*68'),
    ({'tagblock_timestamp': 123456789, 'tagblock_station': 'test'}, 'c:123456789,s:test*1B'),
    ({'tagblock_timestamp': 123456789,
      'tagblock_station': 'test',
      'tagblock_sentence': 1}, 'c:123456789,s:test*1B'),
    ({'tagblock_timestamp': 123456789,
      'tagblock_station': 'test',
      'tagblock_sentence': 1,
      'tagblock_groupsize': 2,
      'tagblock_id': 3}, 'c:123456789,s:test,g:1-2-3*5A'),
])
def test_encode_tagblock(fields, expected):
    assert expected == tagblock.encode_tagblock(**fields)


@pytest.mark.parametrize("tagblock_str,expected", [
    ('*00', {}),
    ('z:123*70', {'z': '123'}),
    ('r:123*78', {'tagblock_relative_time': 123}),
    ('c:123456789*68', {'tagblock_timestamp': 123456789}),
    ('c:123456789,s:test,g:1-2-3*5A',
     {'tagblock_timestamp': 123456789,
      'tagblock_station': 'test',
      'tagblock_sentence': 1,
      'tagblock_groupsize': 2,
      'tagblock_id': 3}),
])
def test_decode_tagblock(tagblock_str, expected):
    assert expected == tagblock.decode_tagblock(tagblock_str)
    assert expected == tagblock.decode_tagblock(tagblock_str, validate_checksum=True)


@pytest.mark.parametrize("tagblock_str", [
    ('z:123*00'),
    ('c:123456789,s:invalid,g:1-2-3*5A'),
    ('c:123456789,s:invalid,g:1-2-3'),
    ('c:123456789,s:invalid,g:1-2-3*ZZ'),
    ('s:missing-tagblock-checksum,q:u,c:1509502436,T:2017-11-01 02.13.56')
])
def test_decode_tagblock_invalid_checksum(tagblock_str):
    with pytest.raises(DecodeError, match='Invalid checksum'):
        tagblock.decode_tagblock(tagblock_str, validate_checksum=True)


@pytest.mark.parametrize("tagblock_str", [
    ('invalid'),
    ('c:invalid'),
    ('c:123456789,z'),
])
def test_decode_tagblock_invalid(tagblock_str):
    with pytest.raises(DecodeError, match='Unable to decode tagblock string'):
        tagblock.decode_tagblock(tagblock_str, validate_checksum=False)


@pytest.mark.parametrize("tagblock_str,new_fields,expected", [
    ('!AIVDM', {'q':123}, '\\q:123*7B\\!AIVDM'),
    ('\\!AIVDM', {'q':123}, '\\q:123*7B\\!AIVDM'),
    ('\\s:00*00\\!AIVDM', {'tagblock_station':99}, '\\s:99*49\\!AIVDM'),
    ('\\s:00*00\\!AIVDM\\s:00*00\\!AIVDM', {'tagblock_station':99}, '\\s:99*49\\!AIVDM\\s:00*00\\!AIVDM'),
    ('\\c:123456789*68\\!AIVDM', {}, '\\c:123456789*68\\!AIVDM'),
    ('\\c:123456789*68\\!AIVDM', {'tagblock_station':99}, '\\c:123456789,s:99*0D\\!AIVDM'),
    ('\\c:123456789*68\\!AIVDM', {'q':123}, '\\c:123456789,q:123*3F\\!AIVDM'),
])
def test_update_tagblock(tagblock_str, new_fields, expected):
    assert expected == tagblock.update_tagblock(tagblock_str, **new_fields)