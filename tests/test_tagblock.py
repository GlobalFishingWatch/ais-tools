import pytest
from datetime import datetime

from ais_tools import tagblock

# NMEA = [
#     '!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49',
#     '!AIVDM,1,1,,B,15O0TWP1h0J>uK:@@MgCA9TD00Ru,0*32',
#     '!AIVDM,2,1,7,A,55PH6Ml000000000000<OCGK;<0000000000000k10613t0002P00000,0*5E',
#     '!AIVDM,2,2,7,A,000000000000000,2*23'
# ]
#
#
# # make sure that our sample nmea messages parse correctly
# def test_nmea():
#     for sentence in NMEA:
#         t, nmea = tagblock.parseTagBlock(sentence)
#         self.assertEqual(sentence, nmea)
#         self.assertTrue(tagblock.isChecksumValid(nmea))


@pytest.mark.parametrize("line,expected", [
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
def test_safe_tagblock_timestamp(line, expected):
    assert tagblock.safe_tagblock_timestamp(line) == expected


@pytest.mark.parametrize("station,timestamp,add_tagblock_t,expected", [
    ('sta', 1, None, 'c:1000,s:sta*5B'),
    ('sta', 1, True, 'c:1000,s:sta,T:1969-12-31 19.00.01*36'),
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
    ('c:1000,s:new*5B', '\\c:1000,s:old*5B\\!AIVDM', True, "\\c:1000,s:new*5B\\!AIVDM"),
    ('c:1000,s:new*5B', '\\c:1000,s:old*5B\\!AIVDM', False, "\\c:1000,s:old*5B\\!AIVDM"),
])
def test_add_tagblock(t, nmea, overwrite, expected):
    assert expected == tagblock.add_tagblock(t, nmea, overwrite)


# def test_add_tagblock():
#     station = 'station'
#     for sentence in NMEA:
#         t, nmea = tagblock.parseTagBlock(tagblock.add_tagblock(sentence, station))
#         assert tagblock.isChecksumValid(nmea)
#         assert station == t['tagblock_station']
#         c = tagblock.tagblock_t(datetime.fromtimestamp(t['tagblock_timestamp']))
#         assert c == t['tagblock_T']

