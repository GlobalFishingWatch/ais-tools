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
        schema_fields = {f.name for f in table.schema}
        extra_fields = {k: v for k, v in message.items() if k not in schema_fields}
        if extra_fields:
            message = {k: v for k, v in message.items() if k not in extra_fields}
            message['extra'] = json.dumps(extra_fields)

        errors = bigquery_client.insert_rows(table, [message])
        if errors:
            raise Exception(errors)

        print("Message insert to {} succeeded".format(table_name))

    except Exception as e:
        print(message or data_in or '<empty message>')
        print("Message insert to {} failed - {}: {}".format(table_name, e.__class__.__name__, str(e)))
        raise
