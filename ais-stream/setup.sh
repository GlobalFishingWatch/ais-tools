#!/bin/bash

THIS_SCRIPT_DIR="$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )"
source ${THIS_SCRIPT_DIR}/config.sh

gcloud pubsub topics create ${NMEA_PUBSUB_TOPIC}
gcloud pubsub topics create ${DECODE_PUBSUB_TOPIC}

${THIS_SCRIPT_DIR}/deploy.sh