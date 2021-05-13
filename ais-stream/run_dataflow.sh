PROJECT_NAME=world-fishing-827
PUBSUB_TOPIC=scratch-paul-dataflow-test
TEMP_BUCKET=scratch-paul-ttl100
OUTPUT_PATH=gs://scratch-paul-ttl100/dataflow_test/output
OUTPUT_TABLE="scratch_paul_ais_stream.raw_decoded_test_3"
SCHEMA=./bigquery-schema.json
#DATAFLOW_RUNNER=DataflowRunner
DATAFLOW_RUNNER=DirectRunner


python dataflow_decode.py \
  --project=${PROJECT_NAME} \
  --input_topic=projects/${PROJECT_NAME}/topics/${PUBSUB_TOPIC} \
  --output_path=${OUTPUT_PATH} \
  --output_table=${OUTPUT_TABLE} \
  --output_schema=${SCHEMA} \
  --runner=${DATAFLOW_RUNNER} \
  --window_size=2 \
  --temp_location=gs://${TEMP_BUCKET}/temp \
  --region=us-central1 \
  --setup_file=../setup.py


