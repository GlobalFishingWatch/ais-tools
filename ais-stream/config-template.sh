#!/bin/bash

#TODO: Set project id
GCP_PROJECT=[GCP Project ID]

#TODO: Set service account.  The service account should have Pub/Sub Publisher and BigQuery Data Editor roles
SERVICE_ACCOUNT=[service account email]

PREFIX=dev-test-ais-stream

NMEA_PUBSUB_TOPIC=projects/${GCP_PROJECT}/topics/${PREFIX}-nmea
NMEA_PUBSUB_SUBSCRIPTION=projects/${GCP_PROJECT}/subscriptions/${PREFIX}-nmea-debug
NMEA_CLOUDFUNC=${PREFIX}-nmea

DECODE_PUBSUB_TOPIC=projects/${GCP_PROJECT}/topics/${PREFIX}-decode
DECODE_PUBSUB_SUBSCRIPTION=projects/${GCP_PROJECT}/subscriptions/${PREFIX}-decode-debug
DECODE_CLOUDFUNC=${PREFIX}-decode

BIGQUERY_DATASET=${GCP_PROJECT}:${PREFIX//-/_}
BIGQUERY_TABLE=${BIGQUERY_DATASET}.raw_decoded
BIGQUERY_CLOUDFUNC=${PREFIX}-bqstore

DEFAULT_SOURCE=${PREFIX}ais-stream-nmea