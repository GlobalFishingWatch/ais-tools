from ais_tools import normalize
from ais_tools import shiptypes

DEFAULT_MAPPED_FIELDS = (
    # (old_key, new_key, transform fn)
    ('uuid', 'msgid', lambda x: x),
    ('mmsi', 'ssvid', str),
    ('id', 'type', normalize.normalize_message_type),
    ('tagblock_timestamp', 'timestamp', normalize.timestamp_to_rfc3339),
    ('source', 'source', lambda x: x),
    ('tagblock_station', 'receiver', lambda x: x),
    ('x', 'lon', normalize.normalize_longitude),
    ('y', 'lat', normalize.normalize_latitude),
    ('sog', 'speed', normalize.normalize_speed),
    ('cog', 'course', normalize.normalize_course_heading),
    ('true_heading', 'heading', normalize.normalize_course_heading),
    ('name', 'shipname', normalize.normalize_text_field),
    ('callsign', 'callsign', normalize.normalize_text_field),
    ('destination', 'destination', normalize.normalize_text_field),
    ('imo_num', 'imo', normalize.normalize_imo),
    ('nav_status', 'status', lambda x: x),
    ('unit_flag', 'class_b_cs_flag', lambda x: x),
)

DEFAULT_FIELD_TRANSFORMS = (
    ('*', normalize.normalize_mapped_fields, {'mapped_fields': DEFAULT_MAPPED_FIELDS}),
    ('length', normalize.normalize_length, {}),
    ('width', normalize.normalize_width, {}),
    ('shiptype', normalize.normalize_shiptype, {'ship_types': shiptypes.SHIPTYPE_MAP}),
    ('dedup_key', normalize.normalize_dedup_key, {})
)


def normalize_and_filter_messages(messages, transforms = DEFAULT_FIELD_TRANSFORMS):
    yield from map(lambda message: normalize.normalize_message(message, transforms),
                   filter(normalize.filter_message, messages))
