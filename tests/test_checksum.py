import pytest

from ais_tools.checksum import checksum
from ais_tools.checksum import checksum_str
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
    actual = checksum_str(str)

    assert actual == expected
    if len(str) > 1:
        assert actual == checksumStr(str)

