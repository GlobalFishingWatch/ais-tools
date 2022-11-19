import pytest

from ais_tools.checksum import checksum
from ais_tools.checksum import is_checksum_valid
from ais_tools.checksum import checksumstr
from ais.stream.checksum import checksumStr


@pytest.mark.parametrize("str,expected", [
    ('test', 22),
    ('XYZ', 91),
    ('0', 48),
    ('', 0),
])
def test_checksum(str, expected):
    assert checksum(str) == expected


@pytest.mark.parametrize("str,expected", [
    ('test', '16'),
    ('XYZ', '5B'),
    ('0', '30'),
    ('', '00'),
])
def test_checksum_str(str, expected):
    actual = checksumstr(str)

    assert actual == expected
    if len(str) > 1:
        assert actual == checksumStr(str)


@pytest.mark.parametrize("str,expected", [
    ("", False),
    ("*", False),
    ("4", False),
    ("40", False),
    ("*40", False),
    ("nochecksum", False),
    ("partialchecksum*", False),
    ("partialchecksum*2", False),
    ("!AIVDM,1,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0*09", True),
    ("!AIVDM,11,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0*09", False),
    ("c:1000,s:old*5A", True),
    ("\\c:1000,s:old*5A", True)
])
def test_is_checksum_valid(str, expected):
    assert is_checksum_valid(str) == expected
