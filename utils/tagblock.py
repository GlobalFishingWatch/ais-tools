import click
from datetime import datetime
import re

#  \g:1-2-73874,n:157036,s:r003669945,c:1241544035*4A\
TAGBLOCK_T_FORMAT = '%Y-%m-%d %H.%M.%S'


def format_tagblock_t(dt):
    return dt.strftime(TAGBLOCK_T_FORMAT)


def compute_checksum(sentence):
    """Compute the NMEA checksum for a payload."""
    checksum = 0
    for char in sentence:
        checksum ^= ord(char)
    checksum_str = '%02x' % checksum
    return checksum_str.upper()


def add_tagblock(nmea, station):
    dt = datetime.utcnow()
    params = dict(
        c=round(dt.timestamp()*1000),
        s=station,
        T=format_tagblock_t(dt)
    )
    param_str = ','.join(["{}:{}".format(k, v) for k,v in params.items()])
    checksum = compute_checksum(param_str)
    return '\\{}*{}\\{}'.format(param_str, checksum, nmea)


def extract_nmea(line):
    match = re.search('(!AIVDM[^*]*\\*[0-9a-fA-F]{2})', line)
    return match.group(0) if match is not None else None


@click.command(
    help="Utility for wrapping a stream of raw AIVDM sentences, such as from the output of aisdeco2, "
         "and prepending a tgblock."
         "\n\n"
         "INPUT should be a text stream with one NMEA message per line, and defaiults to stdin.  Use '-' to explicitly "
         "use stdin"
         "\n\n"
         "OUTPUT is a text stream of the input NMEA with a tgbblock prepended, including fields containing the current "
         "timestamp"
         "\n\n"
         "For example:"
         "\n\n"
         "$ echo '!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49' | python tagblock.py"
         "\n\n"
         "outputs something like"
         "\n\n"
         "\\c:1577762601537,s:sdr-experiments,T:2019-12-30 22.23.21*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49"
         )
@click.argument('input',  type=click.File('r'), default='-')
@click.argument('output', type=click.File('w'), default='-')
@click.option('-s', '--station', default='sdr-experiments',
              help="identifier for this receiving station.  Useful for filtering when  ais feeds from "
                   "multiple receivers are merged")
def tagblock(input, output, station):

    while True:
        line = input.readline()
        if not line:
            break
        nmea = extract_nmea(line)
        if nmea:
            output.write(add_tagblock(nmea, station))
            output.write('\n')


if __name__ == '__main__':
    tagblock()
