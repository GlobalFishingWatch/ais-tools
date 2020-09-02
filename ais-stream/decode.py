import json
import base64

from config import load_config
from ais_tools import aivdm


def handle_event(event, context, pubsub_client):
    data_in = message_in = None

    try:
        config = load_config()
        data_in = base64.b64decode(event.get('data', u'')).decode('utf-8')
        message_in = json.loads(data_in)

        if 'nmea' not in message_in:
            raise Exception("missing nmea field")
        if 'source' not in message_in:
            message_in['source'] = config['DEFAULT_SOURCE']

        message_out = message_in
        message_out.update(aivdm.safe_decode_message(message_in['nmea']))

        data_out = json.dumps(message_out).encode("utf-8")
        pubsub_client.publish(config['DECODE_PUBSUB_TOPIC'], data=data_out, source=message_out['source'])

        if 'error' in message_out:
            print("Message decode failed - {error}".format(**message_out))
        else:
            print("Message decode succeeded")
        print(message_out)

    except Exception as e:
        print(message_in or data_in or '<empty message>')
        print("Message decode failed - {}: {}".format(e.__class__.__name__, str(e)))
        raise
