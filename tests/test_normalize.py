import pytest
from ais_tools.normalize import timestamp_to_rfc3339
from ais_tools.normalize import normalize_longitude
from ais_tools.normalize import normalize_latitude
from ais_tools.normalize import normalize_course_heading
from ais_tools.normalize import normalize_speed
from ais_tools.normalize import normalize_text_field
from ais_tools.normalize import normalize_imo
from ais_tools.normalize import normalize_length
from ais_tools.normalize import normalize_width
from ais_tools.normalize import filter_message
from ais_tools.normalize import normalize_message_type
from ais_tools.normalize import normalize_dedup_key
from ais_tools.normalize import normalize_shiptype
from ais_tools.normalize import normalize_message
from ais_tools.normalize_transform import normalize_and_filter_messages
from ais_tools.normalize_transform import DEFAULT_FIELD_TRANSFORMS
from ais_tools.shiptypes import SHIPTYPE_MAP


@pytest.mark.parametrize("t,expected", [
    (1672531200, '2023-01-01T00:00:00Z', ),
    (1672531200.0, '2023-01-01T00:00:00Z', ),
    (1672531200.123, '2023-01-01T00:00:00Z'),
    (0, '1970-01-01T00:00:00Z'),
])
def test_timestamp_to_rfc3339(t, expected):
    assert timestamp_to_rfc3339(t) == expected


@pytest.mark.parametrize("value,precision,expected", [
    (0, None, 0),
    (1.23456789, None, 1.23457),
    (1.23456789, 2, 1.23),
    (-180, None, -180),
    (-180.0, None, -180.0),
    (180, None, 180),
    (180.0, None, 180.0),
    (181, None, None),
    (999, None, None),
    (-181, None, None),
])
def test_normalize_longitude(value, precision, expected):
    if precision is not None:
        actual = normalize_longitude(value, precision)
    else:
        actual = normalize_longitude(value)
    assert actual == expected


@pytest.mark.parametrize("value,precision,expected", [
    (0, None, 0),
    (1.23456789, None, 1.23457),
    (1.23456789, 2, 1.23),
    (-90, None, -90),
    (-90.0, None, -90.0),
    (90, None, 90),
    (90.0, None, 90.0),
    (91, None, None),
    (999, None, None),
    (-91, None, None),
])
def test_normalize_latitude(value, precision, expected):
    if precision is not None:
        actual = normalize_latitude(value, precision)
    else:
        actual = normalize_latitude(value)
    assert actual == expected


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
def test_normalize_course_heading(value, expected):
    assert normalize_course_heading(value) == expected


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
    assert normalize_speed(value) == expected


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
    assert normalize_speed(value) == expected


@pytest.mark.parametrize("value,expected", [
    ('', None),
    ('@', None),
    ('@@@@@', None),
    ('@@Test', 'Test'),
    ('Test@@', 'Test'),
    ('@This@is@a@test@', 'This@is@a@test'),
])
def test_normalize_text_field(value, expected):
    assert normalize_text_field(value) == expected


@pytest.mark.parametrize("value,expected", [
    (0, None),
    (1, 1),
    (1073741823, 1073741823),
    (1073741824, None),
])
def test_normalize_imo(value, expected):
    assert normalize_imo(value) == expected


@pytest.mark.parametrize("value,expected", [
    (0, 'AIS.0'),
    (99, 'AIS.99'),
])
def test_normalize_message_type(value, expected):
    assert normalize_message_type(value) == expected


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
    ({'tagblock_timestamp': 1707443048}, None),
    ({'nmea': '!AIVDM,2,2,2,A,@,0*57', 'tagblock_timestamp': 1707443048}, '745f4bde2318c974'),
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
    ({'x': 1.2345678}, {'lon': 1.23457}),
    ({'y': 1.2345678}, {'lat': 1.23457}),
    ({'sog': 1.2345678}, {'speed': 1.2}),
    ({'cog': 1.2345678}, {'course': 1.2}),
    ({'true_heading': 1.2345678}, {'heading': 1.2}),
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

