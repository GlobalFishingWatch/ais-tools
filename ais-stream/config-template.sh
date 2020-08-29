#!/bin/bash

#TODO: Set project id
GCP_PROJECT=[GCP Project ID]

#TODO: Set service account.  The service account should have Pub/Sub Publisher and BigQuery Data Editor roles
SERVICE_ACCOUNT=[service account email]


PREFIX=dev-test-

NMEA_PUBSUB_TOPIC=projects/${GCP_PROJECT}/topics/${PREFIX}ais-stream-nmea
NMEA_PUBSUB_SUBSCRIPTION=projects/${GCP_PROJECT}/topics/${PREFIX}ais-stream-nmea-debug
NMEA_CLOUDFUNC=${PREFIX}ais-stream-nmea

DECODE_PUBSUB_TOPIC=projects/${GCP_PROJECT}/topics/${PREFIX}ais-stream-decode
DECODE_PUBSUB_SUBSCRIPTION=projects/${GCP_PROJECT}/topics/${PREFIX}ais-stream-decode-debug
DECODE_CLOUDFUNC=${PREFIX}ais-stream-decode

BIGQUERY_TABLE=${PREFIX//-/_}ais_stream_raw_decoded

DEFAULT_SOURCE=${PREFIX}ais-stream-nmea