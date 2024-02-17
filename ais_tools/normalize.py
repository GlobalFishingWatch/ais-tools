from typing import Union
from datetime import datetime
import hashlib
import re
from ais_tools.shiptypes import SHIPTYPE_MAP


REGEX_NMEA = re.compile(r'!AIVDM[^*]+\*[0-9A-F]{2}')
SKIP_MESSAGE_IF_FIELD_PRESENT = ['error']
SKIP_MESSAGE_IF_FIELD_ABSENT = ['id', 'mmsi', 'tagblock_timestamp']
AIS_TYPES = frozenset([1, 2, 3, 4, 5, 9, 11, 17, 18, 19, 21, 24, 27])


def timestamp_to_rfc3339(timestamp: Union[float, int]) -> str:
    return datetime.utcfromtimestamp(timestamp).isoformat(timespec='seconds') + 'Z'


def normalize_longitude(value: float, precision: int = 5) -> Union[float, None]:
    if -181 < value < 181:
        return round(value, precision)
    else:
        return None


def normalize_latitude(value: float, precision: int = 5) -> Union[float, None]:
    if -91 < value < 91:
        return round(value, precision)
    else:
        return None


def normalize_course_heading(value: float, precision: int = 1) -> Union[float, None]:
    if 0 <= value < 360:
        return round(value, precision)
    else:
        return None


def normalize_speed(value: float, precision: int = 1) -> Union[float, None]:
    if 0 <= value < 102.3:
        return round(value, precision)
    else:
        return None


def normalize_text_field(value: str) -> Union[str, None]:
    value = value.strip('@')
    if len(value) == 0:
        value = None
    return value


def normalize_imo(value: int) -> Union[int, None]:
    if not(1 <= value < 1073741824):
        value = None
    return value


def normalize_message_type(value: int) -> str:
    return f'AIS.{value}'


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


def normalize_mapped_fields(message: dict, mapped_fields: list):
    return {new_key: fn(message[old_key]) for old_key, new_key, fn in mapped_fields if old_key in message}


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




