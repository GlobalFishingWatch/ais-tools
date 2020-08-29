import json
import base64

from config import load_config


def handle_event(event, context, bigquery_client):
    data_in = message = None

    config = load_config()
    table_name = config['BIGQUERY_TABLE']

    try:
        data_in = base64.b64decode(event.get('data', u'')).decode('utf-8')
        message = json.loads(data_in)

        table = bigquery_client.get_table(table_name)
        errors = bigquery_client.insert_rows(table, [message])
        if len(errors) > 0:
            for e in errors:
                print(e)
        else:
            print("message inserted to {}".format(table_name))

    except Exception as e:
        print("Message insert to {} failed - {}: {}".format(table_name, e.__class__.__name__, str(e)))
        print(message or data_in or '<empty message>')
