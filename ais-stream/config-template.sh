#!/bin/bash

GCP_PROJECT=[GCP Project ID]
SERVICE_ACCOUNT=[service account email]
PREFIX=dev-test-


NMEA_PUBSUB_TOPIC=projects/${GCP_PROJECT}/topics/${PREFIX}ais-stream-nmea
NMEA_CLOUDFUNC=${PREFIX}ais-stream-nmea

DECODE_PUBSUB_TOPIC=projects/${GCP_PROJECT}/topics/${PREFIX}ais-stream-decode
DECODE_CLOUDFUNC=${PREFIX}ais-stream-decode

DEFAULT_SOURCE=${PREFIX}ais-stream-nmea