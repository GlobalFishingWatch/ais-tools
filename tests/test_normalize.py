import pytest
import re

from ais_tools.normalize import normalize_timestamp
from ais_tools.normalize import normalize_longitude
from ais_tools.normalize import normalize_latitude
from ais_tools.normalize import normalize_pos_type
from ais_tools.normalize import normalize_course
from ais_tools.normalize import normalize_heading
from ais_tools.normalize import normalize_speed
from ais_tools.normalize import normalize_text_field
from ais_tools.normalize import normalize_imo
from ais_tools.normalize import normalize_length
from ais_tools.normalize import normalize_width
from ais_tools.normalize import normalize_draught
from ais_tools.normalize import filter_message
from ais_tools.normalize import normalize_message_type
from ais_tools.normalize import normalize_dedup_key
from ais_tools.normalize import normalize_shiptype
from ais_tools.normalize import normalize_message
from ais_tools.normalize_transform import normalize_and_filter_messages
from ais_tools.normalize_transform import DEFAULT_FIELD_TRANSFORMS
from ais_tools.shiptypes import SHIPTYPE_MAP
from ais_tools.normalize import REGEX_NMEA


@pytest.mark.parametrize("t,expected", [
    (1672531200, '2023-01-01T00:00:00Z', ),
    (1672531200.0, '2023-01-01T00:00:00Z', ),
    (1672531200.123, '2023-01-01T00:00:00Z'),
    (0, '1970-01-01T00:00:00Z'),
])
def test_normalize_timestamp(t, expected):
    message = {'tagblock_timestamp': t}
    assert normalize_timestamp(message) == expected


@pytest.mark.parametrize("value,expected", [
    (0, 0),
    (1.23456789, 1.23457),
    (-180, -180),
    (-180., -180.0),
    (180, 180),
    (180.0, 180.0),
    (181, None),
    (999, None),
    (-181, None),
])
def test_normalize_longitude(value, expected):
    message = {'x': value}
    assert normalize_longitude(message) == expected


@pytest.mark.parametrize("value,expected", [
    (0, 0),
    (1.23456789, 1.23457),
    (-90, -90),
    (-90.0, -90.0),
    (90, 90),
    (90.0, 90.0),
    (91, None),
    (999, None),
    (-91, None),
])
def test_normalize_latitude(value, expected):
    message = {'y': value}
    assert normalize_latitude(message) == expected


@pytest.mark.parametrize("x, y, expected", [
    (0, 0, 'VALID'),
    (181, 91, 'UNAVAILABLE'),
    (999, 999, 'INVALID'),
    (None, None, None),
    (181, None, 'INVALID'),
    (999, 0, 'INVALID'),
    (0, 999, 'INVALID'),
])
def test_normalize_pos_type(x, y, expected):
    message = {'x': x, 'y': y}
    assert normalize_pos_type(message) == expected


@pytest.mark.parametrize("value,expected", [
    (0, 0),
    (1.23456789, 1.2),
    (0, 0),
    (-0.0, -0.0),
    (359, 359),
    (359.9, 359.9),
    (360, None),
    (999, None),
    (-0.01, None),
])
def test_normalize_course(value, expected):
    message = {'cog': value}
    assert normalize_course(message) == expected


@pytest.mark.parametrize("value,expected", [
    (0, 0),
    (1.23456789, 1.0),
    (0, 0),
    (-0.0, -0.0),
    (359, 359),
    (360, None),
    (999, None),
    (-0.01, None),
])
def test_normalize_heading(value, expected):
    message = {'true_heading': value}
    assert normalize_heading(message) == expected


@pytest.mark.parametrize("value,expected", [
    (0, 0),
    (1.23456789, 1.2),
    (0, 0),
    (-0.0, -0.0),
    (102.2, 102.2),
    (102.3, None),
    (999, None),
    (-0.01, None),
])
def test_normalize_speed(value, expected):
    message = {'sog': value}
    assert normalize_speed(message) == expected


@pytest.mark.parametrize("value,expected", [
    ('', None),
    ('@', None),
    ('@@@@@', None),
    ('@@Test', 'Test'),
    ('Test@@', 'Test'),
    ('@This@is@a@test@', 'This@is@a@test'),
])
def test_normalize_text_field(value, expected):
    message = {'source_field': value}
    assert normalize_text_field(message, source_field='source_field') == expected


@pytest.mark.parametrize("value,expected", [
    (0, None),
    (1, 1),
    (1073741823, 1073741823),
    (1073741824, None),
])
def test_normalize_imo(value, expected):
    message = {'imo_num': value}
    assert normalize_imo(message) == expected


@pytest.mark.parametrize("value,expected", [
    (0, 'AIS.0'),
    (99, 'AIS.99'),
])
def test_normalize_message_type(value, expected):
    message = {'id': value}
    assert normalize_message_type(message) == expected


@pytest.mark.parametrize("message,expected", [
    ({}, None),
    ({'dim_a': 1}, None),
    ({'dim_a': 1, 'dim_b': 1}, 2),
])
def test_normalize_length(message, expected):
    assert normalize_length(message) == expected


@pytest.mark.parametrize("message,expected", [
    ({}, None),
    ({'dim_c': 1}, None),
    ({'dim_c': 1, 'dim_d': 1}, 2),
])
def test_normalize_width(message, expected):
    assert normalize_width(message) == expected


@pytest.mark.parametrize("message,expected", [
    ({}, None),
    ({'draught': 0}, None),
    ({'draught': 1}, 1),
])
def test_normalize_draught(message, expected):
    assert normalize_draught(message) == expected


@pytest.mark.parametrize("value, expected", [
    ('!AIVDM,2,2,2,A,@,0*57', ['!AIVDM,2,2,2,A,@,0*57']),
    ('Not-included!AIVDM,2,2,2,A,@,0*57Also-not-included', ['!AIVDM,2,2,2,A,@,0*57']),
    ('!AIVDM,2,2,2,A,@,0*57not-included!AIVDM,2,2,2,A,@,0*57', ['!AIVDM,2,2,2,A,@,0*57', '!AIVDM,2,2,2,A,@,0*57']),
    ('!BSVDM,2,2,2,A,@,0*57', ['!BSVDM,2,2,2,A,@,0*57']),
    ('!ABVDM,2,2,2,A,@,0*57', ['!ABVDM,2,2,2,A,@,0*57']),
])
def test_nmea_regex(value, expected):
    assert re.findall(REGEX_NMEA, value) == expected


@pytest.mark.parametrize("message,expected", [
    ({'tagblock_timestamp': 1707443048}, None),
    ({'nmea': '!AIVDM,2,2,2,A,@,0*57', 'tagblock_timestamp': 1707443048}, '745f4bde2318c974'),
    ({'nmea': '!BSVDM,2,2,2,A,@,0*57', 'tagblock_timestamp': 1707443048}, 'a6926b3f62eeb7d7'),
    ({'nmea': '!BSVDM,2,2,2,B,@,0*57', 'tagblock_timestamp': 1707443048}, 'd3972916d1a17048'),
    ({'nmea': 'invalid', 'tagblock_timestamp': 1707443048}, None),
    ({"nmea": "!AIVDM,1,1,,A,H69@rrS3S?SR3G2D000000000000,0*2e",
      "tagblock_timestamp": 1712156268}, '06f1f1b00815aa10'),
])
def test_normalize_dedup_key(message, expected):
    assert normalize_dedup_key(message) == expected


@pytest.mark.parametrize("message,expected", [
    ({}, None),
    ({'type_and_cargo': 30}, 'Fishing'),
])
def test_normalize_shiptype(message, expected):
    assert normalize_shiptype(message, SHIPTYPE_MAP) == expected


@pytest.mark.parametrize("message,expected", [
    ({'error': ''}, False),
    ({'id': 1}, False),
    ({'id': 1, 'mmsi': '123'}, False),
    ({'id': 1, 'mmsi': '123', 'tagblock_timestamp': 123}, False),
    ({'id': 1, 'mmsi': '123', 'tagblock_timestamp': 946684800}, True),
    ({'id': 8, 'mmsi': '123', 'tagblock_timestamp': 946684800}, False),
    ({'id': 1, 'mmsi': '123', 'tagblock_timestamp': 946684800, 'error': 'err'}, False),
])
def test_filter_message(message, expected):
    assert filter_message(message) == expected


@pytest.mark.parametrize("message,expected", [
    ({}, {}),
    ({'uuid': '123'}, {'msgid': '123'}),
    ({'mmsi': 123}, {'ssvid': '123'}),
    ({'id': 1}, {'type': 'AIS.1'}),
    ({'tagblock_timestamp': 946684800}, {'timestamp': '2000-01-01T00:00:00Z'}),
    ({'source': 'spire'}, {'source': 'spire'}),
    ({'tagblock_station': 'A123'}, {'receiver': 'A123'}),
    ({'x': 1.2345678, 'y': 1.2345678}, {'lon': 1.23457, 'lat': 1.23457, 'pos_type': 'VALID'}),
    ({'x': 1.2345678}, {'lon': 1.23457, 'pos_type': 'INVALID'}),
    ({'x': 181, 'y': 91}, {'pos_type': 'UNAVAILABLE'}),
    ({'sog': 1.2345678}, {'speed': 1.2}),
    ({'cog': 1.2345678}, {'course': 1.2}),
    ({'true_heading': 1.2345678}, {'heading': 1.0}),
    ({'name': 'boaty@@@'}, {'shipname': 'boaty'}),
    ({'callsign': 'BMBF123@@@'}, {'callsign': 'BMBF123'}),
    ({'destination': 'OZ@@@'}, {'destination': 'OZ'}),
    ({'imo_num': 999}, {'imo': 999}),
    ({'nav_status': 3}, {'status': 3}),
    ({'unit_flag': 1}, {'class_b_cs_flag': 1}),
    ({'type_and_cargo': 30}, {'shiptype': 'Fishing'}),
    ({'dim_a': 1, 'dim_b': 1}, {'length': 2}),
    ({'dim_c': 1, 'dim_d': 1}, {'width': 2}),
    ({'type_and_cargo': 30}, {'shiptype': 'Fishing'}),
    ({'nmea': '!AIVDM,2,2,2,A,@,0*57', 'tagblock_timestamp': 1707443048},
        {'timestamp': '2024-02-09T01:44:08Z', 'dedup_key': '745f4bde2318c974'}),
])
def test_normalize_message(message, expected):
    assert normalize_message(message, DEFAULT_FIELD_TRANSFORMS) == expected


def test_normalize_and_filter_messages():
    messages = [
        {'id': 1, 'mmsi': 1, 'tagblock_timestamp': 946684800},
        {'error': 'drop this one'}
    ]
    expected = [{'type': 'AIS.1', 'ssvid': '1', 'timestamp': '2000-01-01T00:00:00Z'}]
    actual = list(normalize_and_filter_messages(messages))
    assert actual == expected
