#!/bin/bash

gcloud dataflow sql query 'SELECT *

FROM bigquery.table.`world-fishing-827`.scratch_paul_ais_stream.spire_nmea_2020_07_01

LIMIT 1000' \
  --job-name scratch-paul-dataflow-qb-to-pubsub-test-3 \
  --region us-central1 \
  --pubsub-topic projects/world-fishing-827/topics/scratch-paul-dataflow-test
