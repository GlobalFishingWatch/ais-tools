import json

from config import load_config
from flask_api import status

from ais_tools.message import Message


def handle_request(request, pubsub_client):
    try:
        config = load_config()
        message = Message(request.get_json())
        if not message.get('nmea'):
            raise Exception("nmea field is required")
        message = message.add_source(config['DEFAULT_SOURCE']).add_uuid()
        data = json.dumps(message).encode("utf-8")
        pubsub_client.publish(config['NMEA_PUBSUB_TOPIC'], data=data, source=message['source'])
        return "OK"
    except Exception as e:
        return "Not OK - {}".format(str(e)), status.HTTP_400_BAD_REQUEST
