from typing import Optional, Any
from datetime import datetime, timezone
import xxhash
import re
from enum import Enum


REGEX_NMEA = re.compile(r'!(?:AB|AI|AN|BS)VD[MO][^*]+\*[0-9A-Fa-f]{2}')
SKIP_MESSAGE_IF_FIELD_PRESENT = ['error']
SKIP_MESSAGE_IF_FIELD_ABSENT = ['id', 'mmsi', 'tagblock_timestamp']
AIS_TYPES = frozenset([1, 2, 3, 4, 5, 9, 11, 17, 18, 19, 21, 24, 27])
POSITION_TYPE = Enum('PositionType', ['NULL', 'VALID', 'UNAVAILABLE', 'INVALID'])


def normalize_ssvid(message: dict) -> Optional[str]:
    value = message.get('mmsi')
    if value is not None:
        return str(value)
    else:
        return None


def normalize_timestamp(message: dict) -> Optional[str]:
    # convert to RFC3339 string
    t = message.get('tagblock_timestamp')
    if t is not None:
        t = datetime.fromtimestamp(t, tz=timezone.utc)
        return t.isoformat(timespec='seconds').replace("+00:00", "Z")
    else:
        return None


def normalize_tx_timestamp(message: dict) -> Optional[str]:
    def in_range(value, valid_range):
        return value is not None and valid_range[0] <= value <= valid_range[1]

    fields = {
        'year': (1, 9999),
        'month': (1, 12),
        'day': (1, 31),
        'hour': (0, 23),
        'minute': (0, 59),
        'second': (0, 59)
    }
    values = [(f, message.get(f), valid_range) for f, valid_range in fields.items()]
    if all(in_range(value, valid_range) for _, value, valid_range in values):
        values = {f: value for f, value, _ in values}
        try:
            return datetime(**values).isoformat(timespec='seconds') + 'Z'
        except ValueError:
            return None


def coord_type(val: float, _min: float, _max: float, unavailable: float) -> POSITION_TYPE:
    if val is None:
        return POSITION_TYPE.NULL
    elif _min <= val <= _max:
        return POSITION_TYPE.VALID
    elif val == unavailable:
        return POSITION_TYPE.UNAVAILABLE
    else:
        return POSITION_TYPE.INVALID


def normalize_longitude(message: dict) -> Optional[float]:
    if coord_type(val := message.get('x'), -180, 180, 181) == POSITION_TYPE.VALID:
        return round(val, 5)
    else:
        return None


def normalize_latitude(message: dict) -> Optional[float]:
    if coord_type(val := message.get('y'), -90, 90, 91) == POSITION_TYPE.VALID:
        return round(val, 5)
    else:
        return None


def normalize_pos_type(message: dict) -> Optional[str]:
    x_type = coord_type(message.get('x'), -180, 180, 181)
    y_type = coord_type(message.get('y'), -90, 90, 91)

    if x_type == y_type:
        result = x_type.name
    else:
        result = POSITION_TYPE.INVALID.name
    return result if result != 'NULL' else None


def normalize_course(message: dict) -> Optional[float]:
    value = message.get('cog')
    if value is not None and 0 <= value <= 359.9:
        return round(value, 1)
    else:
        return None


def normalize_heading(message: dict) -> Optional[float]:
    value = message.get('true_heading')
    if value is not None and 0 <= value <= 359:
        return round(value, 0)
    else:
        return None


def normalize_speed(message: dict) -> Optional[float]:
    value = message.get('sog')
    if value is not None and 0.0 <= value <= 102.2:
        return round(value, 1)
    else:
        return None


def normalize_text_field(message: dict, source_field: str = None) -> Optional[str]:
    value = message.get(source_field)
    if value is not None:
        value = value.strip('@')
        if len(value) == 0:
            value = None
    return value


def normalize_imo(message: dict) -> Optional[int]:
    value = message.get('imo_num')
    if value is not None and not(1 <= value < 1073741824):
        value = None
    return value


def normalize_message_type(message: dict) -> Optional[str]:
    value = message.get('id')
    if value is not None:
        return f'AIS.{value}'
    else:
        return value


def normalize_length(message: dict) -> Optional[int]:
    dim_a = message.get('dim_a')
    dim_b = message.get('dim_b')
    if dim_a is not None and dim_b is not None:
        return dim_a + dim_b
    return None


def normalize_width(message: dict) -> Optional[int]:
    dim_c = message.get('dim_c')
    dim_d = message.get('dim_d')
    if dim_c is not None and dim_d is not None:
        return dim_c + dim_d
    return None


def normalize_draught(message: dict) -> Optional[float]:
    draught = message.get('draught')
    if draught is not None and draught > 0:
        return draught
    return None


def normalize_shiptype(message: dict, ship_types) -> Optional[str]:
    return ship_types.get(message.get('type_and_cargo'))


def normalize_dedup_key(message: dict) -> Optional[str]:
    """
    Compute a key using nmea and timestamp. This can be used later for deduplication of messages
    that come late or from multiple sources. Tf the same nmea occurs in the same minute it is either
    a true duplicate or you can probably live without it anyway
    """

    if 'nmea' not in message or 'tagblock_timestamp' not in message:
        return None

    nmea = ''.join(REGEX_NMEA.findall(message['nmea']))
    if not nmea:
        return None     # no nmea found in message

    timestamp = int(message['tagblock_timestamp'] / 60)

    key = f'{nmea}_{timestamp}'.encode('utf-8')
    return xxhash.xxh3_64_hexdigest(key)


def map_field(message: dict, source_field: str = None) -> Optional[Any]:
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
