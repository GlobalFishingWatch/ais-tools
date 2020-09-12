import os


def load_config():
    return dict(
            GCP_PROJECT=os.environ.get('GCP_PROJECT'),
            NMEA_PUBSUB_TOPIC=os.environ.get('NMEA_PUBSUB_TOPIC', 'Must specify a pubsub topic in env vars'),
            DECODE_PUBSUB_TOPIC=os.environ.get('DECODE_PUBSUB_TOPIC', 'Must specify a pubsub topic in env vars'),
            BIGQUERY_TABLE=os.environ.get('BIGQUERY_TABLE', 'Must specify a BQ table in env vars'),
            DEFAULT_SOURCE=os.environ.get('DEFAULT_SOURCE', 'undefined')
    )
