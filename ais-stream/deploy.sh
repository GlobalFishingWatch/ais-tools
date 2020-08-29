#!/bin/bash
set -e

THIS_SCRIPT_DIR="$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )"
source ${THIS_SCRIPT_DIR}/config.sh


echo "Deploying cloud function from ${THIS_SCRIPT_DIR} to ${NMEA_CLOUDFUNC} "
gcloud functions deploy ${NMEA_CLOUDFUNC} \
  --entry-point=ais_stream_nmea_http \
  --runtime=python37 \
  --trigger-http \
  --set-env-vars NMEA_PUBSUB_TOPIC=${NMEA_PUBSUB_TOPIC} \
  --set-env-vars DEFAULT_SOURCE=${DEFAULT_SOURCE} \
  --allow-unauthenticated \
  --service-account=${SERVICE_ACCOUNT} \
  --source=${THIS_SCRIPT_DIR}


echo "Deploying cloud function from ${THIS_SCRIPT_DIR} to ${DECODE_CLOUDFUNC}"
gcloud functions deploy ${DECODE_CLOUDFUNC} \
  --entry-point=ais_stream_decode_pubsub \
  --runtime=python37 \
  --trigger-topic=$(echo ${NMEA_PUBSUB_TOPIC} | cut -f4 -d/)  \
  --set-env-vars DECODE_PUBSUB_TOPIC=${DECODE_PUBSUB_TOPIC} \
  --set-env-vars DEFAULT_SOURCE=${DEFAULT_SOURCE} \
  --service-account=${SERVICE_ACCOUNT} \
  --source=${THIS_SCRIPT_DIR}