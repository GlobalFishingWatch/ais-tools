from google.cloud import pubsub_v1
from google.cloud import bigquery

import nmea
import decode
import bqstore


pubsub_client = pubsub_v1.PublisherClient()
bigquery_client = bigquery.Client()


def ais_stream_nmea_http(request):
    return nmea.handle_request(request, pubsub_client)


def ais_stream_decode_pubsub(event, context):
    return decode.handle_event(event, context, pubsub_client)


def ais_stream_bigquery_pubsub(event, context):
    return bqstore.handle_event(event, context, bigquery_client)

