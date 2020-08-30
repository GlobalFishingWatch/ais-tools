from ais_tools import cloud
from unittest.mock import Mock


def test_message_to_http():
    session = Mock()
    cloud.requests_retry_session = Mock(return_value=session)
    url = 'https://domain/endpoint'
    message = {}
    res, message = cloud.message_to_http(message, url)

    session.post.assert_called_once()
    session.post.assert_called_with(url, json=message)


