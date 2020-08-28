from google.cloud import pubsub_v1
import nmea
import decode


pubsub_client = pubsub_v1.PublisherClient()


def ais_stream_nmea_http(request):
    return nmea.handle_request(request, pubsub_client)


def ais_stream_decode_pubsub(event, context):
    return decode.handle_event(event, context)

