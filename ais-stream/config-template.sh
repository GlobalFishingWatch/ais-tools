#!/bin/bash

# Copy this file to config.sh and edit the variables below

#TODO: Set project id
GCP_PROJECT=[GCP Project ID]

#TODO: Set service account.  The service account should have Pub/Sub Publisher and BigQuery Data Editor roles
SERVICE_ACCOUNT=[service account email]

#TODO: Set the prefix to be used for naming things.  This will be used for everything that is created in GCP
#      including cloud functions, pubsub topics and bigquery datasets
PREFIX=dev-test-ais-stream

#TODO: Set the source label that will be assigned to incoming AIS messages if no source is provided
DEFAULT_SOURCE=${PREFIX}-nmea


# OPTIONAL - Other names of things that you probably don't need to change
NMEA_PUBSUB_TOPIC=projects/${GCP_PROJECT}/topics/${PREFIX}-nmea
NMEA_PUBSUB_SUBSCRIPTION=projects/${GCP_PROJECT}/subscriptions/${PREFIX}-nmea-debug
NMEA_CLOUDFUNC=${PREFIX}-nmea

DECODE_PUBSUB_TOPIC=projects/${GCP_PROJECT}/topics/${PREFIX}-decode
DECODE_PUBSUB_SUBSCRIPTION=projects/${GCP_PROJECT}/subscriptions/${PREFIX}-decode-debug
DECODE_CLOUDFUNC=${PREFIX}-decode

BIGQUERY_DATASET=${GCP_PROJECT}:${PREFIX//-/_}
BIGQUERY_TABLE=${BIGQUERY_DATASET}.raw_decoded
BIGQUERY_CLOUDFUNC=${PREFIX}-bqstore

