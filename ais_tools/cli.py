"""
Command-line interface for ais-tools.
"""

import click
import json

import ais_tools
from ais_tools import message
from ais_tools import cloud
from ais_tools.aivdm import AIVDM
from ais_tools import tagblock
from ais_tools.nmea import safe_join_multipart_stream
from ais_tools.nmea import join_multipart_stream
from ais_tools.message import Message


@click.group(invoke_without_command=True)
# @click.group()
@click.option('-v', '--version', is_flag=True, help='Display version number and exit')
@click.pass_context
def cli(ctx, version):
    if version:
        click.echo('Version: {}'.format(ais_tools.__version__))

    # invoked without a command
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command(
    help="Stream NMEA messages to cloud ais-stream API"
)
@click.argument('url', )
@click.argument('input', type=click.File('r'), default='-')
@click.option('-s', '--source', default='ais_tools',
              help="identifier for the source of this AIS stream"
                   "eg. orbcomm | spire | ais_receiver_123")
@click.option('-o', '--overwrite', is_flag=True,
              help="replace any source value that already exists in the input stream")
def cloud_stream(input, url, source, overwrite):
    messages = message.message_stream(input, source, overwrite)
    for res, msg in cloud.message_to_http_stream(messages, url=url):
        print(res.text, res.status_code)


@cli.command(
    short_help="Prepend a tagblock to AIVDM messages",
    help="Utility for wrapping a stream of raw AIVDM sentences, such as from the output of aisdeco2, "
         "and prepending a tagblock."
         "\n\n"
         "INPUT should be a text stream with one NMEA message per line, and defaults to stdin.  Use '-' to explicitly "
         "use stdin"
         "\n\n"
         "OUTPUT is a text stream of the input NMEA with a tagblock prepended, including fields containing the current "
         "timestamp"
         "\n\n"
         "For example:"
         "\n\n"
         "$ echo '!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49' | \\"
         "  ais_tools add-tagblock -s my-station"
         "\n\n"
         "outputs something like"
         "\n\n"
         "\\c:1577762601537,s:my-station,T:2019-12-30 22.23.21*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49"
)
@click.argument('input', type=click.File('r'), default='-')
@click.argument('output', type=click.File('w'), default='-')
@click.option('-s', '--station', default='ais_tools',
              help="identifier for this receiving station.  Useful for filtering when  ais feeds from "
                   "multiple receivers are merged")
def add_tagblock(input, output, station):
    for nmea in input:
        t = tagblock.create_tagblock(station)
        output.write(tagblock.add_tagblock(t, nmea.strip()))
        output.write('\n')


@cli.command(
    short_help="Update existing tagblock with specified field values.  Create a new tagblock if none is present",
    help="Utility for updating a stream of raw AIVDM sentences with tagblocks, modifying the tagblock to"
         "add or overwrite selected fields "
         "\n\n"
         "INPUT should be a text stream with one NMEA message per line, and defaults to stdin.  Use '-' to explicitly "
         "use stdin"
         "\n\n"
         "OUTPUT is a text stream of the input NMEA with modified tagblock"
         "\n\n"
         "For example:"
         "\n\n"
         "$ echo '\\c:1577762601537,s:99\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49' | \\"
         "  ais_tools update-tagblock -s my-station"
         "\n\n"
         "outputs something like"
         "\n\n"
         "\\c:1577762601537,s:my-station*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49"
)
@click.argument('input', type=click.File('r'), default='-')
@click.argument('output', type=click.File('w'), default='-')
@click.option('-s', '--station',
              help="identifier for the receiving station")
@click.option('-t', '--text',
              help="tagblock text field")
def update_tagblock(input, output, station, text):
    fields = {'tagblock_station': station, 'tagblock_text': text}
    fields = {k: v for k, v in fields.items() if v is not None}
    for nmea in input:
        output.write(tagblock.safe_update_tagblock(nmea.strip(), **fields))
        output.write('\n')


@cli.command(
    short_help="Decode AIS from NMEA to JSON",
    help="Decode AIS from NMEA to JSON"
         "\n\n"
         "INPUT should be a text stream with one NMEA message per line, and defaults to stdin.  Use '-' to explicitly "
         "use stdin"
         "\n\n"
         "OUTPUT is a text stream of the decoded messages as newline JSON with a field schema compatible with libais. "
         "The original nmea from the input stream is included in each message in a field 'nmea'. "
         "For messages that fail to parse, the original message is output in a JSON object with a field 'error' that "
         "contains the decoding error message"
         "\n\n"
)
@click.argument('input', type=click.File('r'), default='-')
@click.argument('output', type=click.File('w'), default='-')
@click.option('-q', '--quiet', is_flag=True, help="Do not emit decode errors to console")
def decode(input, output, quiet):
    decoder = AIVDM()
    for msg in Message.stream(input):
        msg = decoder.safe_decode(msg)
        if not quiet and  'error' in msg:
            click.echo(msg['error'], err=True)
        output.write(json.dumps(msg))
        output.write('\n')


@cli.command(
    short_help="Encode AIS from JSON to NMEA",
    help="Encode AIS from JSON to NMEA"
         "\n\n"
         "INPUT should be a text stream of newline JSON, and defaults to stdin.  Use '-' to explicitly "
         "use stdin"
         "\n\n"
         "OUTPUT is a text stream of the input NMEA with a tagblock prepended, including fields containing the current "
         "timestamp"
         "\n\n"
)
@click.argument('input', type=click.File('r'), default='-')
@click.argument('output', type=click.File('w'), default='-')
def encode(input, output):
    encoder = AIVDM()
    for msg in Message.stream(input):
        msg = encoder.safe_encode(msg)
        if 'error' in msg:
            click.echo(msg['error'], err=True)
        output.write(msg.nmea)
        output.write('\n')


@cli.command(
    short_help="Run performance benchmarks",
    help="Run a suite of benchmarks and display a results table showing throughput for the main operations."
)
def benchmark():
    from ais_tools.benchmark import run_benchmarks, format_results
    results = run_benchmarks()
    click.echo(format_results(results))


@cli.command(
    short_help="Match up multipart nmea messages",
    help="Match up multipart nmea messages\n" + join_multipart_stream.__doc__)
@click.argument('input', type=click.File('r'), default='-')
@click.argument('output', type=click.File('w'), default='-')
@click.option('-t', '--max-time', default=500,
              help="Retain an unmatched message part in the buffer until at least max_time milliseconds have"
                   "elapsed since the message part was added to the buffer"
              )
@click.option('-c', '--max-count', default=100,
              help="Retain an unmatched message part in the buffer until at least max_count messages have"
                   "been seen after the message part was added to the buffer"
              )
def join_multipart(input, output, max_time, max_count):
    for nmea in safe_join_multipart_stream(input,
                                           max_time_window=max_time,
                                           max_message_window=max_count):
        output.write(nmea)
        output.write('\n')
