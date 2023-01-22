from datetime import datetime
from datetime import timezone

from ais import DecodeError
from ais_tools.checksum import checksumstr
from ais_tools.checksum import is_checksum_valid

# import warnings
# with warnings.catch_warnings():
#     warnings.simplefilter("ignore")
#     from ais.stream import parseTagBlock                # noqa: F401

TAGBLOCK_T_FORMAT = '%Y-%m-%d %H.%M.%S'


def safe_tagblock_timestamp(line):
    """
    attempt to extract the tagblock timestamp without triggering any exceptions
    This is used for reporting messages that fail to decode
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


def create_tagblock(station, timestamp=None, add_tagblock_t=True):
    t = timestamp or datetime.now().timestamp()
    params = dict(
        c=round(t*1000),
        s=station,
    )
    if add_tagblock_t:
        params['T'] = datetime.fromtimestamp(t, tz=timezone.utc).strftime(TAGBLOCK_T_FORMAT)
    param_str = ','.join(["{}:{}".format(k, v) for k, v in params.items()])
    return '{}*{}'.format(param_str, checksumstr(param_str))


def split_tagblock(nmea):
    """
    Split off the tagblock from the rest of the message

    Note that if the nmea is a concatenated multipart message then only the tagblock of
    the first message will be split off
    """
    tagblock = ''
    if nmea.startswith("\\") and not nmea.startswith("\\!"):
        parts = nmea[1:].split("\\", 1)
        if len(parts) == 2:
            tagblock, nmea = parts
    return tagblock, nmea


def join_tagblock(tagblock, nmea):
    """
    Join a tagblock to an AIVDM message that does not already have a tagblock
    """
    if tagblock and nmea:
        return "\\{}\\{}".format(tagblock.lstrip('\\'), nmea.lstrip('\\'))
    else:
        return "{}{}".format(tagblock, nmea)


def add_tagblock(tagblock, nmea, overwrite=True):
    """
    Add a tagblock to an nmea message.  If a tagblock iis already present,
    replace it if overwrite is True and do nothing if overwrite is False
    """

    existing_tagblock, nmea = split_tagblock(nmea)
    if existing_tagblock and not overwrite:
        tagblock = existing_tagblock

    return join_tagblock(tagblock, nmea)


tagblock_fields = {
    'c': 'tagblock_timestamp',
    'n': 'tagblock_line_count',
    'r': 'tagblock_relative_time',
    'd': 'tagblock_destination',
    's': 'tagblock_station',
    't': 'tagblock_text',
}

tagblock_fields_reversed = {v: k for k, v in tagblock_fields.items()}

tagblock_group_fields = ["tagblock_sentence", "tagblock_groupsize", "tagblock_id"]


def encode_tagblock(**kwargs):
    group_fields = {}
    fields = {}

    for k, v in kwargs.items():
        if k in tagblock_group_fields:
            group_fields[k] = str(v)
        elif k in tagblock_fields_reversed:
            fields[tagblock_fields_reversed[k]] = v
        else:
            fields[k.replace('tagblock_', '')] = v

    if len(group_fields) == 3:
        fields['g'] = '-'.join([group_fields[k] for k in tagblock_group_fields])

    base_str = ','.join(["{}:{}".format(k, v) for k, v in fields.items()])
    return '{}*{}'.format(base_str, checksumstr(base_str))


def decode_tagblock(tagblock_str, validate_checksum=False):

    tagblock = tagblock_str.rsplit("*", 1)[0]

    fields = {}

    if not tagblock:
        return fields

    if validate_checksum and not is_checksum_valid(tagblock_str):
        raise DecodeError('Invalid checksum')

    for field in tagblock.split(","):
        try:
            key, value = field.split(":")

            if key == 'g':
                parts = [int(part) for part in value.split("-") if part]
                if len(parts) != 3:
                    raise DecodeError('Unable to decode tagblock group')
                fields.update(dict(zip(tagblock_group_fields, parts)))
            else:
                if key in ['n', 'r']:
                    value = int(value)
                elif key == 'c':
                    value = int(value)
                    if value > 40000000000:
                        value = value / 1000.0

                fields[tagblock_fields.get(key, key)] = value
        except ValueError:
            raise DecodeError('Unable to decode tagblock string')

    return fields


def update_tagblock(nmea, **kwargs):
    tagblock_str, nmea = split_tagblock(nmea)
    tagblock = decode_tagblock(tagblock_str)
    tagblock.update(kwargs)
    tagblock_str = encode_tagblock(**tagblock)
    return join_tagblock(tagblock_str, nmea)


def safe_update_tagblock(nmea, **kwargs):
    try:
        nmea = update_tagblock(nmea, **kwargs)
    except DecodeError:
        pass
    return nmea
