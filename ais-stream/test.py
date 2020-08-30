import pytest
from unittest.mock import Mock
import json
import base64

import nmea
import decode
import bqstore

# NB: cannot test main.py because it imports google.cloud.pubsub_v1 on load, which requires auth
# so put all the functionality into separate modules and test them


@pytest.fixture(scope="function", autouse=True)
def env_vars(monkeypatch):
    env_vars = dict(
        NMEA_PUBSUB_TOPIC="NMEA_PUBSUB_TOPIC",
        DECODE_PUBSUB_TOPIC="DECODE_PUBSUB_TOPIC",
        BIGQUERY_TABLE="BIGQUERY_TABLE",
        DEFAULT_SOURCE='DEFAULT_SOURCE'
    )
    for k, v in env_vars.items():
        monkeypatch.setenv(k, v)
    return env_vars


@pytest.fixture(scope="function", autouse=True)
def pubsub_context():
    mock_context = Mock()
    mock_context.event_id = '617187464135194'
    mock_context.timestamp = '2019-07-15T22:09:03.761Z'
    return mock_context


@pytest.fixture(scope="function", autouse=True)
def pubsub_client():
    mock_client = Mock()
    return mock_client


@pytest.fixture(scope="function", autouse=True)
def bigquery_client():

    # Need to do this little trick to mock the 'name' attribute of a schema field
    # see https://docs.python.org/3/library/unittest.mock.html#mock-names-and-the-name-attribute
    def mock_with_name(name):
        mock = Mock()
        mock.name = name
        return mock

    schema_fields = ['nmea', 'source']
    schema = [mock_with_name(name) for name in schema_fields]
    table = Mock(schema=schema)
    attrs = {'insert_rows.return_value': [], 'get_table.return_value': table}
    mock_client = Mock(**attrs)

    return mock_client


def test_nmea(env_vars, pubsub_client):

    data = {'nmea': 'NMEA_MESSAGE', 'source': 'source'}
    request = Mock(get_json=Mock(return_value=data), args=data)

    assert 'OK' == nmea.handle_request(request, pubsub_client)

    pubsub_client.publish.assert_called_once()
    pubsub_client.publish.assert_called_with(
        env_vars['NMEA_PUBSUB_TOPIC'],
        data=json.dumps(data).encode("utf-8"),
        source=data['source']
    )


def test_nmea_empty(pubsub_client):

    data = {}
    request = Mock(get_json=Mock(return_value=data), args=data)

    assert ('Not OK - nmea field is required', 400) == nmea.handle_request(request, pubsub_client)
    assert not pubsub_client.publish.called


def test_decode_empty(capsys, pubsub_context, pubsub_client):
    event = {}

    with pytest.raises(json.JSONDecodeError):
        decode.handle_event(event, pubsub_context, pubsub_client)
    out, err = capsys.readouterr()
    assert 'JSONDecodeError' in out


@pytest.mark.parametrize(
    "message,log_output,pubsub_output",
    [
        ({}, 'missing nmea field', None),
        ({'nmea': '!AIVDM1234567*89'}, ['!AIVDM', 'DEFAULT_SOURCE'], {'source': 'DEFAULT_SOURCE'}),
        ({'nmea': '!AIVDM1234567*89', 'source': 'my_source'}, 'my_source', {'source': 'my_source'}),
        ({'nmea': '!AIVDM1234567*89'}, ['failed'], {'error': 'Invalid checksum'}),
        ({'nmea': '!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49'}, ['succeeded'], {"mmsi": 367596940}),
    ]
)
def test_decode(capsys, env_vars, pubsub_context, pubsub_client, message, log_output, pubsub_output):
    event = {'data': base64.b64encode(json.dumps(message).encode())}

    if pubsub_output is None:
        with pytest.raises(Exception):
            decode.handle_event(event, pubsub_context, pubsub_client)
    else:
        decode.handle_event(event, pubsub_context, pubsub_client)

    out, err = capsys.readouterr()

    print(out)

    # test that log output contains the expected strings somewhere
    if isinstance(log_output, str):
        log_output = [log_output]
    for expected in log_output:
        assert expected in out

    # test whether a message was published to pubsub, and if so, it has the expected content
    if not pubsub_output:
        assert not pubsub_client.publish.called
    else:
        pubsub_client.publish.assert_called_once()
        args, kwargs = pubsub_client.publish.call_args
        assert args == (env_vars['DECODE_PUBSUB_TOPIC'],)
        assert kwargs['source'] == message.get('source', env_vars['DEFAULT_SOURCE'])
        actual_subset = {k: v for k, v in json.loads(kwargs['data']).items() if k in pubsub_output}
        assert actual_subset == pubsub_output


@pytest.mark.parametrize(
    "message,expected",
    [
        ({}, {}),
        ({'nmea': '!AIVDM1234567*89'}, {'nmea': '!AIVDM1234567*89'}),
        ({'nmea': '!AIVDM1234567*89', 'not_in_schema': 'value'},
         {'nmea': '!AIVDM1234567*89', 'extra': '{"not_in_schema": "value"}'}),
    ]
)
def test_bqstore(capsys, env_vars, pubsub_context, bigquery_client, message, expected):
    event = {'data': base64.b64encode(json.dumps(message).encode())}
    bqstore.handle_event(event, pubsub_context, bigquery_client)
    out, err = capsys.readouterr()

    assert 'succeeded' in out

    bigquery_client.get_table.assert_called_once()
    bigquery_client.get_table.assert_called_with(env_vars['BIGQUERY_TABLE'])

    bigquery_client.insert_rows.assert_called_once()
    name, args, kwargs = bigquery_client.insert_rows.mock_calls[0]
    assert args[1] == [expected]
