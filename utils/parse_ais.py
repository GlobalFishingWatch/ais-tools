import click
import json
import unittest
import ais
import warnings
from ais import DecodeError
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from ais import stream as ais_stream


def safe_tagblock_timestamp(line):
    """
    attempt to extract the tagblock timestamp without triggering any exceptions
    This is used for reporting messages that fail to parse
    returns 0 if no timestamp can be found
    """

    try:
        if line.startswith("\\"):
            tagblock = line[1:].split("\\", 1)[0]
            tagblock = tagblock.split("*")[0]
            for field in tagblock.split(","):
                parts = field.split(":")
                if len(parts) == 2:
                    key, value = parts
                    if key == 'c':
                        t = int(value)
                        return t if t <= 40000000000 else t/1000
    except ValueError:
        pass

    return 0


def parse_message(line):

    msg = dict()

    try:
        tagblock, nmea = ais_stream.parseTagBlock(line)
        msg.update(tagblock)
        msg['nmea'] = nmea

        if not ais_stream.checksum.isChecksumValid(nmea):
            raise DecodeError('Invalid checksum')

        # TODO: handle multi-sentence messages
        fields = nmea.split(',')
        assert int(fields[1]) == 1, 'must be a single sentence message'

        body = fields[5]
        pad = int(nmea.split('*')[0][-1])
        # print(body, pad)
        msg.update(ais.decode(body, pad))

    except DecodeError as e:
        msg['error'] = str(e)

    return msg


def parse_stream(test_stream):
    for line in test_stream:
        try:
            yield parse_message(line)
        except DecodeError as e:
            yield error_message(line)
            print(str(e))
            pass


def format_messages(messages, fmt):
    for msg in messages:
        yield json.dumps(msg)


@click.command(
    help="Utility for parsing a stream of AIS NMEA-encoded messages."
         "\n\n"
         "INPUT should be a text stream with one NMEA message per line, and defaiults to stdin.  "
         "Use '-' to explicitly use stdin"
         "\n\n"
         "OUTPUT is a text stream of the parsed NMEA.  Use '-' for stdout "
         "\n\n"
         "For example:"
         "\n\n"
         "$ echo '\\c:1577762601537,s:sdr-experiments,T:2019-12-30 22.23.21*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49' | python parse_ais.py"
         "\n\n"
         "outputs something like"
         "\n\n"
         '{"tagblock_timestamp": 1577762601.537, "tagblock_station": "sdr-experiments", "tagblock_T": "2019-12-30 22.23.21", "nmea": "!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49\n", "id": 1, "repeat_indicator": 0, "mmsi": 367596940, "nav_status": 0, "rot_over_range": true, "rot": -731.386474609375, "sog": 0.0, "position_accuracy": 0, "x": -80.62191666666666, "y": 28.408531666666665, "cog": 11.800000190734863, "true_heading": 511, "timestamp": 10, "special_manoeuvre": 0, "spare": 0, "raim": false, "sync_state": 0, "slot_timeout": 5, "received_stations": 29}'
         "\n\n"
         ""
         )
@click.argument('input', type=click.File('r'), default='-')
@click.argument('output', type=click.File('w'), default='-')
@click.option('-f', '--format', 'fmt',
              type=click.Choice(['JSON'], case_sensitive=False),
              default='JSON',
              help="output format.   JSON is newline delimited JSON, one object per message "
              )
def parse(input, output, fmt):
    for msg in format_messages(parse_stream(input), fmt):
        output.write(msg)
        output.write('\n')


if __name__ == '__main__':
    parse()
