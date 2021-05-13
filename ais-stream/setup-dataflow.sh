gcloud pubsub topics create scratch-paul-dataflow-test
gcloud scheduler jobs create pubsub scratch-paul-dataflow-test-cron --schedule="* * * * *" \
  --topic=scratch-paul-dataflow-test --message-body="Daquwaka"
gcloud scheduler jobs run scratch-paul-dataflow-test-cron

