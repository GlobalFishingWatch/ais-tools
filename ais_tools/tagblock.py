from datetime import datetime
from datetime import timezone
import re

from ais_tools.checksum import checksumstr

import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    # from ais.stream.checksum import isChecksumValid     # noqa: F401
    # from ais.stream.checksum import checksumStr
    from ais.stream import parseTagBlock                # noqa: F401

TAGBLOCK_T_FORMAT = '%Y-%m-%d %H.%M.%S'
nmeaChecksumRegExStr = r"""\,[0-9]\*[0-9A-F][0-9A-F]"""
nmeaChecksumRE = re.compile(nmeaChecksumRegExStr)


def isChecksumValid(nmeaStr, allowTailData=True):
    """Return True if the string checks out with the checksum.

    @param allowTailData: Permit handing of Coast Guard format with data after the checksum
    @param data: NMEA message.  Leading ?/! are optional
    @type data: str
    @return: True if the checksum matches
    @rtype: bool

    >>> isChecksumValid("!AIVDM,1,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0*09")
    True

    Corrupted:

    >>> isChecksumValid("!AIVDM,11,1,,B,35MsUdPOh8JwI:0HUwquiIFH21>i,0*09")
    False
    """

    if allowTailData:
        match = nmeaChecksumRE.search(nmeaStr)
        if not match:
            return False
        nmeaStr = nmeaStr[:match.end()]

    if nmeaStr[-3] != '*':
        return False  # Bad string without proper checksum.
    checksum = nmeaStr[-2:]
    if checksum.upper() == checksumstr(nmeaStr):
        return True
    return False


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
        tagblock, nmea = nmea[1:].split("\\", 1)
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
