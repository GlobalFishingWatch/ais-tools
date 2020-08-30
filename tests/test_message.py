import pytest
from ais_tools import message
import itertools as it


def test_gfw_uuid():
    assert str(message.GFW_UUID('test')) == 'c3757317-71ed-5251-bec6-fa01f05cb8dc'


@pytest.mark.parametrize("msg,expected", [
    ('', {'nmea': ''}),
    ('!AIVDM1234567*89', {'nmea': '!AIVDM1234567*89'}),
    ({'nmea': '!AIVDM1234567*89'}, {'nmea': '!AIVDM1234567*89'}),
    ('{"nmea": "!AIVDM1234567*89"}', {'nmea': '!AIVDM1234567*89'}),
])
def test_as_dict(msg, expected):
    assert message.as_dict(msg) == expected


@pytest.mark.parametrize("msg", [
    42,
    "{not valid JSON}"
])
def test_as_dict_fail(msg):
    with pytest.raises(ValueError):
        message.as_dict(msg)


@pytest.mark.parametrize("msg,source,overwrite,expected", [
    ({}, 'source', False, {'source': 'source'}),
    ({'source': 'old'}, 'new', False, {'source': 'old'}),
    ({'source': 'old'}, 'new', True, {'source': 'new'}),
])
def test_add_source(msg, source, overwrite, expected):
    assert message.add_source(msg, source, overwrite) == expected

    repeat = 3
    messages = list(message.add_source_stream(it.repeat(msg, repeat), source, overwrite))
    assert len(messages) == repeat
    for m in messages:
        assert m == expected


@pytest.mark.parametrize("msg,overwrite,expected", [
    ({}, False, {'uuid': '7b16d688-bafc-55ad-8f2b-ca76c2a4eb4f'}),
    ({'nmea': '!AVIDM123'}, False, {'nmea': '!AVIDM123', 'uuid': 'a40aa816-9e5b-5d39-bed4-eecf791af8e1'}),
    ({'nmea': '!AVIDM123', 'uuid': 'old'}, False, {'nmea': '!AVIDM123', 'uuid': 'old'}),
    ({'nmea': '!AVIDM123', 'uuid': 'old'}, True, {'nmea': '!AVIDM123', 'uuid': 'a40aa816-9e5b-5d39-bed4-eecf791af8e1'}),
])
def test_add_uuid(msg, overwrite, expected):
    assert message.add_uuid(msg, overwrite) == expected

    repeat = 3
    messages = list(message.add_uuid_stream(it.repeat(msg, repeat), overwrite))
    assert len(messages) == repeat
    for m in messages:
        assert m == expected



@pytest.mark.parametrize("msg", [
    ({}),
    ({'nmea': '!AVIDM123'}),
    (''),
    ('!AVIDM123'),
    ('{}'),
    ('{"nmea": "!AVIDM123"}')
    ])
@pytest.mark.parametrize("repeat", [0, 1, 2])
def test_message_stream_input_type(msg, repeat):
    m = msg.copy() if isinstance(msg, dict) else msg
    messages = message.message_stream(it.repeat(m, repeat))
    assert len(list(messages)) == repeat


@pytest.mark.parametrize("old_source", [None, 'old'])
@pytest.mark.parametrize("new_source", [None, 'new'])
@pytest.mark.parametrize("overwrite", [True, False])
def test_message_stream_source(old_source, new_source, overwrite):
    messages = [{'nmea': '!AVIDM123', 'source': old_source}]

    if (overwrite and new_source) or (old_source is None):
        expected = new_source
    else:
        expected = old_source
    messages = message.message_stream(messages, source=new_source, overwrite=overwrite)
    for m in messages:
        assert m.get('source') == expected


@pytest.mark.parametrize("old_uuid", ['old', None])
@pytest.mark.parametrize("add_uuid", [True, False])
@pytest.mark.parametrize("overwrite", [True, False])
def test_message_stream_add_uuid(old_uuid, add_uuid, overwrite):

    messages = [{'nmea': '!AVIDM123', 'source': 'test', 'uuid': old_uuid}]

    if add_uuid and (overwrite or old_uuid is None):
        expected = '0ce10f94-d475-5f50-826f-23541125f73a'
    else:
        expected = old_uuid
    messages = message.message_stream(messages, add_uuid=add_uuid, overwrite=overwrite)
    for m in messages:
        assert m.get('uuid') == expected


# @pytest.mark.parametrize("msg", [
#     ({}),
#     ({'nmea': '!AVIDM123'}),
#     ({'nmea': '!AVIDM123', 'source': 'unchanged'}),
#     ({'nmea': '!AVIDM123', 'source': 'unchanged', 'uuid': 'unchanged'}),
#     ('!AVIDM123'),
#     ('{"nmea": "!AVIDM123"}')
#     ])
# @pytest.mark.parametrize("overwrite", [True, False])
# @pytest.mark.parametrize("source", [None, 'new_source'])
# @pytest.mark.parametrize("add_uuid", [True, False])
# @pytest.mark.parametrize("repeat", [0, 1, 2])
# def test_message_stream(msg, overwrite, source, add_uuid, repeat):
#     m = msg.copy() if isinstance(msg, dict) else msg
#     messages = message.message_stream(
#         it.repeat(m, repeat),
#         source=source,
#         add_uuid=add_uuid,
#         overwrite=overwrite)
#     messages = list(messages)
#     assert len(messages) == repeat
#     if source and (overwrite or ('source' not in msg)):
#         source_expected = source
#     else:
#         source_expected = msg.get('source')
#
#     for m in messages:
#         assert m.get('source') == source_expected
