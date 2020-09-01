# AIS Stream Tools

A collection of tools for streaming AIS in Google Cloud Platform

## Testing 

This will test the cloud function code (local unit tests only)

```console
pytest
```

## Deploy to GCP
First make a copy of config-template.sh and update the default values
```console
cp config-template.sh config.sh
nano config.sh
```

Now install everything into GCP with 
```console
./setup.py
```

This will create pubsub topics, a bigquery dataset and table, and deploy the cloud functions

If you modify the cloud function code, you can re-deploy them with
```console
./deploy.sh
```

To tear down the deployment, use

```console
# WARNING: THIS WILL DELETE EVERYTHING!
./teardown.sh
```

## Architecture/Flow

```diagram
+-------------------+
| ais-stream-nmea   |
| cloudfunc         |
| trigger: HTTP     |
|                   |
|   * nmea          |
|   * source        |
+-------+-----------+
        |
        v
+-------+-----------+
| ais-stream-nmea   |
| Pubsub topic      |
|                   |
|   * nmea          |
|   * source        |
+-------+-----------+
        |
        v
+-------+-----------+
| ais-stream-decode |
| cloudfunc         |
| trigger: pubsub   |
|                   |
|   * nmea          |
|   * source        |
|   * message       |
+-------+-----------+
        |
        v
+-------+-----------+
| ais-stream-decode |
| Pubsub topic      |
|                   |
|   * nmea          |
|   * source        |
|   * message       |
|   * error         |
|                   |
+-------+-----------+
        |
        v
+-------+-----------+
| ais-stream-decode |
| Bigquery Table    |
|                   |
|   * nmea          |
|   * source        |
|   * message       |
|   * error         |
|                   |
+-------------------+
```