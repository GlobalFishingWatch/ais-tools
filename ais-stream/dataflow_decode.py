import argparse
import datetime
import json
import logging


import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import apache_beam.transforms.window as window
# from apache_beam.io.gcp.internal.clients import bigquery
# from apache_beam.io.gcp.bigquery_tools import BigQueryWrapper

from ais_tools.aivdm import AIVDM
from ais_tools.message import Message


decoder = AIVDM()


class GroupWindowsIntoBatches(beam.PTransform):
    """A composite transform that groups Pub/Sub messages based on publish
    time and outputs a list of dictionaries, where each contains one message
    and its publish timestamp.
    """

    def __init__(self, window_size):
        # Convert minutes into seconds.
        self.window_size = int(window_size * 60)

    def expand(self, pcoll):
        return (
            pcoll
            # Assigns window info to each Pub/Sub message based on its
            # publish timestamp.
            | "Window into Fixed Intervals"
            >> beam.WindowInto(window.FixedWindows(self.window_size))

            # | "Add timestamps to messages" >> beam.ParDo(AddTimestamps())

            # Use a dummy key to group the elements in the same window.
            # Note that all the elements in one window must fit into memory
            # for this. If the windowed elements do not fit into memory,
            # please consider using `beam.util.BatchElements`.
            # https://beam.apache.org/releases/pydoc/current/apache_beam.transforms.util.html#apache_beam.transforms.util.BatchElements
            | "Add Dummy Key" >> beam.Map(lambda elem: (None, elem))
            | "Groupby" >> beam.GroupByKey()
            | "Abandon Dummy Key" >> beam.MapTuple(lambda _, val: val)
            # | "Abandon Dummy Key" >> beam.FlatMap(lambda val: val[1])
        )


class AddTimestamps(beam.DoFn):
    def process(self, element, publish_time=beam.DoFn.TimestampParam):
        """Processes each incoming windowed element by extracting the Pub/Sub
        message and its publish timestamp into a dictionary. `publish_time`
        defaults to the publish timestamp returned by the Pub/Sub server. It
        is bound to each element by Beam at runtime.
        """

        element['decode_time'] = datetime.datetime.utcfromtimestamp(
                float(publish_time)
            ).strftime("%Y-%m-%d %H:%M:%S.%f"),
        yield element


class DecodeNMEA(beam.DoFn):
    def __init__(self, schema, source='ais-tools'):
        self.schema = schema
        self.source = source

    def process(self, element):
        """Decode the nmea element in the message body
        """

        message = Message(element.decode("utf-8"))
        message.update(decoder.safe_decode(message.get('nmea')))
        message.add_source(self.source)
        message.add_uuid()

        schema_fields = {f['name'] for f in self.schema['fields']}
        extra_fields = {k: v for k, v in message.items() if k not in schema_fields}
        if extra_fields:
            message = {k: v for k, v in message.items() if k not in extra_fields}
            message['extra'] = json.dumps(extra_fields)

        yield message


class WriteBatchesToGCS(beam.DoFn):
    def __init__(self, output_path):
        self.output_path = output_path

    def process(self, batch, window=beam.DoFn.WindowParam):
        """Write one batch per file to a Google Cloud Storage bucket. """

        ts_format = "%H:%M"
        window_start = window.start.to_utc_datetime().strftime(ts_format)
        window_end = window.end.to_utc_datetime().strftime(ts_format)
        filename = "-".join([self.output_path, window_start, window_end])

        with beam.io.gcp.gcsio.GcsIO().open(filename=filename, mode="w") as f:
            for element in batch:
                f.write("{}\n".format(json.dumps(element)).encode("utf-8"))


def run(input_topic, output_path, output_table, output_schema, window_size=1.0, pipeline_args=None):
    # `save_main_session` is set to true because some DoFn's rely on
    # globally imported modules.
    pipeline_options = PipelineOptions(
        pipeline_args, streaming=True, save_main_session=True
    )

    with beam.Pipeline(options=pipeline_options) as pipeline:
        (
            pipeline
            | "Read PubSub Messages" >> beam.io.ReadFromPubSub(topic=input_topic)
            # | beam.Create([
            # {'nmea':'!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49'.encode("utf-8"),
            #     '!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49'.encode("utf-8")
            # ])
            | "Decode nmea" >> beam.ParDo(DecodeNMEA(output_schema))
            | "Window into" >> GroupWindowsIntoBatches(window_size)
            # | "Write to BigQuery" >> beam.io.WriteToBigQuery(
            #     table=output_table,
            #     schema=output_schema,
            #     write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            #     create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED)
            | "Write to GCS" >> beam.ParDo(WriteBatchesToGCS(output_path))
        )


if __name__ == "__main__":  # noqa
    logging.getLogger().setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_topic",
        help="The Cloud Pub/Sub topic to read from.\n"
        '"projects/<PROJECT_NAME>/topics/<TOPIC_NAME>".',
    )
    parser.add_argument(
        "--window_size",
        type=float,
        default=1.0,
        help="Output file's window size in number of minutes.",
    )
    parser.add_argument(
        "--output_path",
        help="GCS Path of the output file including filename prefix.",
    )
    parser.add_argument(
        "--output_table",
        help="output bigquery table as [dataset].[table]",
    )
    parser.add_argument(
        "--output_schema",
        help="JSON file containing output table schema",
    )
    known_args, pipeline_args = parser.parse_known_args()

    with open(known_args.output_schema) as f:
        output_schema = {'fields': json.load(f)}

    run(
        known_args.input_topic,
        known_args.output_path,
        known_args.output_table,
        output_schema,
        known_args.window_size,
        pipeline_args,
    )
