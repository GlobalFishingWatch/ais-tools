import pytest
import ais_tools
from ais_tools.message import Message
from ais_tools.message import UUID
import itertools as it


def test_uuid():
    assert str(UUID('test')) == '4e782d81-81ae-5eab-93eb-ddb536abd3da'


@pytest.mark.parametrize("msg,expected", [
    ('', {'nmea': ''}),
    ('!AIVDM1234567*89', {'nmea': '!AIVDM1234567*89'}),
    ({'nmea': '!AIVDM1234567*89'}, {'nmea': '!AIVDM1234567*89'}),
    ('{"nmea": "!AIVDM1234567*89"}', {'nmea': '!AIVDM1234567*89'}),
    ('', {'nmea': ''}),
])
def test_message_construct(msg, expected):
    assert Message(msg) == expected


@pytest.mark.parametrize("arg", [
    42,
    ['!AIVDM'],
])
def test_message_construct_fail(arg):
    with pytest.raises(ValueError):
        Message(arg)


def test_message_construct_too_many_args():
    with pytest.raises(ValueError, match='Message can only be constructed with a single positional '
                                         'argument or one or more kwargs'):
        Message(1, 2)


@pytest.mark.parametrize("msg", [
    "{not valid JSON}",
    "{field:value}",
])
def test_message_construct_bad_json(msg):
    assert Message(msg)['error'].startswith('JSONDecodeError')


@pytest.mark.parametrize("msg,source,overwrite,expected", [
    ({}, 'source', False, {'nmea': '', 'source': 'source'}),
    ({'source': 'old'}, 'new', False, {'nmea': '', 'source': 'old'}),
    ({'source': 'old'}, 'new', True, {'nmea': '', 'source': 'new'}),
])
def test_add_source(msg, source, overwrite, expected):
    assert expected == Message(msg).add_source(source, overwrite)


@pytest.mark.parametrize("msg,overwrite,expected", [
    ({}, False, 'c4a4d6e8-ea5f-5af5-8091-9afe3a73f652'),
    ({'nmea': '!AVIDM123'}, False, 'de08b5ee-d5dc-5561-8790-4abfcbd4b953'),
    ({'nmea': '!AVIDM123', 'uuid': 'old'}, False, 'old'),
    ({'nmea': '!AVIDM123', 'uuid': 'old'}, True, 'de08b5ee-d5dc-5561-8790-4abfcbd4b953'),
    ({'nmea': '!AVIDM123', 'tagblock_timestamp': 1598653784}, True, '3c17f7c5-74fd-53af-ac9f-87861c43b217'),
])
def test_add_uuid(msg, overwrite, expected):
    msg = Message(msg).add_uuid(overwrite=overwrite)
    assert msg['uuid'] == expected


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
    messages = Message.stream(it.repeat(m, repeat))
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
    messages = Message.stream(messages)
    for m in messages:
        if new_source:
            m.add_source(new_source, overwrite)
        assert m.get('source') == expected


@pytest.mark.parametrize("old_uuid", ['old', None])
@pytest.mark.parametrize("add_uuid", [True, False])
@pytest.mark.parametrize("overwrite", [True, False])
def test_message_stream_add_uuid(old_uuid, add_uuid, overwrite):

    messages = [{'nmea': '!AVIDM123', 'source': 'test', 'uuid': old_uuid}]

    if add_uuid and (overwrite or old_uuid is None):
        expected = '56cf351b-5e53-52b3-9f36-45a93a7d89ec'
    else:
        expected = old_uuid
    messages = Message.stream(messages)
    for m in messages:
        if add_uuid:
            m.add_uuid(overwrite=overwrite)
        assert m.get('uuid') == expected


def test_add_parser_version():
    message = Message()
    message.add_parser_version()
    assert ais_tools.__version__ in message['parser']
