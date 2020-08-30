#!/bin/bash

THIS_SCRIPT_DIR="$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )"
source ${THIS_SCRIPT_DIR}/config.sh

gcloud pubsub topics create ${NMEA_PUBSUB_TOPIC}
gcloud pubsub subscriptions create \
  ${NMEA_PUBSUB_SUBSCRIPTION} \
  --topic=${NMEA_PUBSUB_TOPIC} \
  --topic-project=${GCP_PROJECT}

gcloud pubsub topics create ${DECODE_PUBSUB_TOPIC}
gcloud pubsub subscriptions create \
  ${DECODE_PUBSUB_SUBSCRIPTION} \
  --topic=${DECODE_PUBSUB_TOPIC} \
  --topic-project=${GCP_PROJECT}

bq mk --dataset  ${BIGQUERY_DATASET}
bq mk --table \
  ${BIGQUERY_TABLE} \
  ${THIS_SCRIPT_DIR}/bigquery-schema.json

${THIS_SCRIPT_DIR}/deploy.sh