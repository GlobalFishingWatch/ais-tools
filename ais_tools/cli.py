import click
import json

from ais_tools import message
from ais_tools import cloud
from ais_tools.aivdm import AIVDM
from ais_tools import tagblock
from ais_tools.nmea import safe_join_multipart_stream


@click.group()
def cli():
    pass


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
     "$ echo '!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49' | ais_tools add_tagblock"
     "\n\n"
     "outputs something like"
     "\n\n"
     "\\c:1577762601537,s:ais-tools,T:2019-12-30 22.23.21*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49"
     )
@click.argument('input',  type=click.File('r'), default='-')
@click.argument('output', type=click.File('w'), default='-')
@click.option('-s', '--station', default='ais_tools',
              help="identifier for this receiving station.  Useful for filtering when  ais feeds from "
                   "multiple receivers are merged")
def add_tagblock(input, output, station):
    for nmea in input:
        t = tagblock.create_tagblock(station)
        output.write(tagblock.add_tagblock(t, nmea))
        output.write('\n')


@cli.command(
    help="Decode AIS from NMEA to JSON"
        "\n\n"
        "INPUT should be a text stream with one NMEA message per line, and defaults to stdin.  Use '-' to explicitly "
        "use stdin"
        "\n\n"
        "OUTPUT is a text stream of the input NMEA with a tagblock prepended, including fields containing the current "
        "timestamp"
        "\n\n"
    )
@click.argument('input',  type=click.File('r'), default='-')
@click.argument('output', type=click.File('w'), default='-')
def decode(input, output):
    decoder = AIVDM()
    for msg in decoder.decode_stream(input):
        output.write(json.dumps(msg))
        output.write('\n')


@cli.command(
    help="Match up multipart nmea messages")
@click.argument('input',  type=click.File('r'), default='-')
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
    for nmea in safe_join_multipart_stream(input, max_time_window=max_time, max_message_window=max_count):
        output.write(nmea)
        output.write('\n')



