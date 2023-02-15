from datetime import datetime
from datetime import timezone

from ais import DecodeError
# from ais_tools.core import checksum_str
from ais_tools.core import is_checksum_valid
from ais_tools import _tagblock
from ais_tools import core


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
    return core.encode_tagblock(params)

    # param_str = ','.join(["{}:{}".format(k, v) for k, v in params.items()])
    # return '{}*{}'.format(param_str, checksum_str(param_str))


def split_tagblock(nmea):
    """
    Split off the tagblock from the rest of the message

    Note that if the nmea is a concatenated multipart message then only the tagblock of
    the first message will be split off
    """
    return core.split_tagblock(nmea)



def join_tagblock(tagblock, nmea):
    """
    Join a tagblock to an AIVDM message that does not already have a tagblock
    """

    return core.join_tagblock(tagblock, nmea)



def add_tagblock(tagblock, nmea, overwrite=True):
    """
    Add a tagblock to an nmea message.  If a tagblock iis already present,
    replace it if overwrite is True and do nothing if overwrite is False
    """

    existing_tagblock, nmea = split_tagblock(nmea)
    if existing_tagblock and not overwrite:
        tagblock = existing_tagblock

    return join_tagblock(tagblock, nmea)


def encode_tagblock(**kwargs):
    try:
        return core.encode_tagblock(kwargs)
    except ValueError as e:
        raise DecodeError(e)


def decode_tagblock(tagblock_str, validate_checksum=False):
    if validate_checksum and not is_checksum_valid(tagblock_str):
        raise DecodeError('Invalid checksum')
    try:
        return core.decode_tagblock(tagblock_str)
    except ValueError as e:
        raise DecodeError(e)


def update_tagblock(nmea, **kwargs):
    return _tagblock.update(nmea, kwargs)

def safe_update_tagblock(nmea, **kwargs):
    try:
        nmea = update_tagblock(nmea, **kwargs)
    except DecodeError:
        pass
    return nmea
