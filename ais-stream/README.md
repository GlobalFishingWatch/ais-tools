# AIS Stream Tools

A collection of tools for streaming AIS in Google Cloud Platform

## Testing

```console
pytest test.py
```

## Deploy to cloud functions
```console
./deploy.sh
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