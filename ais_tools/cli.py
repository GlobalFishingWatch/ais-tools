import click
from ais_tools import message
from ais_tools import cloud


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
    messages = message.message_stream(input)
    for res, msg in cloud.message_to_http_stream(messages, url=url):
        pass


@cli.command(
    help="Utility for wrapping a stream of raw AIVDM sentences, such as from the output of aisdeco2, "
     "and prepending a tgblock."
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
     "\\c:1577762601537,s:sdr-experiments,T:2019-12-30 22.23.21*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49"
     )
@click.argument('input',  type=click.File('r'), default='-')
@click.argument('output', type=click.File('w'), default='-')
@click.option('-s', '--station', default='ais_tools',
              help="identifier for this receiving station.  Useful for filtering when  ais feeds from "
                   "multiple receivers are merged")
def add_tagblock(input, output, station):
    click.echo('command not implemented')


@cli.command()
def decode():
    click.echo('command not implemented')


@cli.command()
def multiline():
    click.echo('command not implemented')
