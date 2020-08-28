import json

from config import load_config
from flask_api import status


def handle_request(request, pubsub_client):
    try:
        config = load_config()
        payload = request.get_json()
        if not payload.get('nmea'):
            raise Exception("nmea field is required")
        if not payload.get('source'):
            payload['source'] = config['DEFAULT_SOURCE']
        data = json.dumps(payload).encode("utf-8")
        pubsub_client.publish(config['NMEA_PUBSUB_TOPIC'], data=data, source=payload['source'])
        return "OK"
    except Exception as e:
        return "Not OK - {}".format(str(e)), status.HTTP_400_BAD_REQUEST
