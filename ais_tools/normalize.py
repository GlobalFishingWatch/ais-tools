from typing import Union
from datetime import datetime
import hashlib
import re
from ais_tools.shiptypes import SHIPTYPE_MAP


REGEX_NMEA = re.compile(r'!AIVDM[^*]+\*[0-9A-F]{2}')
SKIP_MESSAGE_IF_FIELD_PRESENT = ['error']
SKIP_MESSAGE_IF_FIELD_ABSENT = ['id', 'mmsi', 'tagblock_timestamp']
AIS_TYPES = frozenset([1, 2, 3, 4, 5, 9, 11, 17, 18, 19, 21, 24, 27])

def nornalize_ssvid(message: dict) -> Union[str, None]:
    value = message.get('mmsi')
    if value is not None:
        return str(value)
    else:
        return None

def normalize_timestamp(message: dict) -> Union[str, None]:
    # convert to RFC3339 string
    t = message.get('tagblock_timestamp')
    if t is not None:
        return datetime.utcfromtimestamp(message['tagblock_timestamp']).isoformat(timespec='seconds') + 'Z'
    else:
        return None


def normalize_longitude(message: dict) -> Union[float, None]:
    value = message.get('x')
    if value is not None and -181 < value < 181:
        return round(value, 5)
    else:
        return None


def normalize_latitude(message: dict) -> Union[float, None]:
    value = message.get('y')
    if value is not None and -91 < value < 91:
        return round(value, 5)
    else:
        return None


def normalize_course(message: dict) -> Union[float, None]:
    value = message.get('cog')
    if value is not None and 0 <= value <= 359.9:
        return round(value, 1)
    else:
        return None


def normalize_heading(message: dict) -> Union[float, None]:
    value = message.get('true_heading')
    if value is not None and 0 <= value <= 359:
        return round(value, 0)
    else:
        return None


def normalize_speed(message: dict) -> Union[float, None]:
    value = message.get('sog')
    if value is not None and 0.0 <= value <= 102.2:
        return round(value, 1)
    else:
        return None


def normalize_text_field(message: dict, source_field: str = None) -> Union[str, None]:
    value = message.get(source_field)
    if value is not None:
        value = value.strip('@')
        if len(value) == 0:
            value = None
    return value


def normalize_imo(message: dict) -> Union[int, None]:
    value = message.get('imo_num')
    if value is not None and not(1 <= value < 1073741824):
        value = None
    return value


def normalize_message_type(message: dict) -> str:
    value = message.get('id')
    if value is not None:
        return f'AIS.{value}'
    else:
        return value


def normalize_length(message: dict) -> int:
    dim_a = message.get('dim_a')
    dim_b = message.get('dim_b')
    if dim_a is not None and dim_b is not None:
        return dim_a + dim_b
    return None


def normalize_width(message: dict) -> int:
    dim_c = message.get('dim_c')
    dim_d = message.get('dim_d')
    if dim_c is not None and dim_d is not None:
        return dim_c + dim_d
    return None


def normalize_shiptype(message: dict, ship_types) -> str:
    return ship_types.get(message.get('type_and_cargo'))


def normalize_dedup_key(message: dict) -> str:
    """
    Compute a key using nmea and timestamp. This can be used later for deduplication of messages
    that come late or from multiple sources. Tf the same nmea occurs in the same minute it is either
    a true duplicate or you can probably live without it anyway
    """

    if 'nmea' not in message or 'tagblock_timestamp' not in message:
        return None

    nmea = ''.join(re.findall(REGEX_NMEA, message['nmea']))
    timestamp = int(message['tagblock_timestamp'] / 60)

    key = f'{nmea}_{timestamp}'.encode('utf-8')
    h = hashlib.sha1()
    h.update(key)
    return h.hexdigest()[:16]


def map_field(message: dict, source_field: str = None):
    return message.get(source_field)

# def normalize_mapped_fields(message: dict, mapped_fields: list):
#     return {new_key: fn(message[old_key]) for old_key, new_key, fn in mapped_fields if old_key in message}


def filter_message(message) -> bool:
    """
    :param message:  a dict containing an AIS message
    :return: True if the message should be kept and processes, False if the message should be discarded
    """
    return not (
        any(f in message for f in SKIP_MESSAGE_IF_FIELD_PRESENT)
        or not all(f in message for f in SKIP_MESSAGE_IF_FIELD_ABSENT)
        or message['id'] not in AIS_TYPES
        or message['tagblock_timestamp'] < 946684800            # Jan 1 2000 UTC
    )


def normalize_message(message: dict, transforms: list) -> dict:
    new_message = {}
    for key, fn, kwargs in transforms:
        value = fn(message, **kwargs)
        if value is not None:
            if key == '*':
                new_message.update(value)
            else:
                new_message[key] = value
    return new_message




