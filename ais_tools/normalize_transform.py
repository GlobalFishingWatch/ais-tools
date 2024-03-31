from ais_tools import normalize
from ais_tools import shiptypes


DEFAULT_FIELD_TRANSFORMS = (
    ('msgid', normalize.map_field, {'source_field': 'uuid'}),
    ('source', normalize.map_field, {'source_field': 'source'}),
    ('receiver', normalize.map_field, {'source_field': 'tagblock_station'}),
    ('type', normalize.normalize_message_type, {}),
    ('ssvid', normalize.normalize_ssvid, {}),
    ('timestamp', normalize.normalize_timestamp, {}),
    ('lon', normalize.normalize_longitude, {}),
    ('lat', normalize.normalize_latitude, {}),
    ('pos_type', normalize.normalize_pos_type, {}),
    ('course', normalize.normalize_course, {}),
    ('heading', normalize.normalize_heading, {}),
    ('speed', normalize.normalize_speed, {}),
    ('imo', normalize.normalize_imo, {}),
    ('length', normalize.normalize_length, {}),
    ('width', normalize.normalize_width, {}),
    ('draught', normalize.normalize_draught, {}),
    ('shipname', normalize.normalize_text_field, {'source_field': 'name'}),
    ('callsign', normalize.normalize_text_field, {'source_field': 'callsign'}),
    ('destination', normalize.normalize_text_field, {'source_field': 'destination'}),
    ('shiptype', normalize.normalize_shiptype, {'ship_types': shiptypes.SHIPTYPE_MAP}),
    ('status', normalize.map_field, {'source_field': 'nav_status'}),
    ('class_b_cs_flag', normalize.map_field, {'source_field': 'unit_flag'}),
    ('dedup_key', normalize.normalize_dedup_key, {}),
)


def normalize_and_filter_messages(messages, transforms=DEFAULT_FIELD_TRANSFORMS):
    yield from map(lambda message: normalize.normalize_message(message, transforms),
                   filter(normalize.filter_message, messages))
