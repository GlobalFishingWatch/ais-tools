#!/bin/bash

source config.sh

echo "WARNING: This will permanently DELETE pubsub topics and cloud functions"
echo "DELETE these Pubsub topics"
echo "  * ${NMEA_PUBSUB_TOPIC}"
echo "  * ${DECODE_PUBSUB_TOPIC}"
echo "DELETE these cloud functions"
echo "  * ${NMEA_CLOUDFUNC}"
echo "  * ${DECODE_CLOUDFUNC}"
read -p "Are you sure? (y/n)" -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

gcloud pubsub topics delete ${NMEA_PUBSUB_TOPIC}
gcloud pubsub topics delete ${DECODE_PUBSUB_TOPIC}
gcloud functions delete --quiet ${NMEA_CLOUDFUNC}
gcloud functions delete --quiet ${DECODE_CLOUDFUNC}