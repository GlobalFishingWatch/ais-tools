from ais_tools.transcode import NmeaBits
from ais_tools.transcode import NmeaStruct as Struct
from ais_tools.transcode import UintField as Uint
from ais_tools.transcode import Uint10Field as Uint10
from ais_tools.transcode import LatLonField as LatLon
from ais_tools.transcode import BoolField as Bool
from ais_tools.transcode import ASCII6Field as ASCII6


def ais19_decode(body, pad):
    bits = NmeaBits.from_nmea(body, pad)
    message = bits.unpack(ais19_fields)
    message['name'] = message['name_1'] + message['name_2']
    del message['name_1']
    del message['name_2']

    return message


def ais19_encode(message):
    bits = NmeaBits(ais19_fields.nbits)

    message['name_1'] = message['name'][:10]
    message['name_2'] = message['name'][10:]

    bits.pack(ais19_fields, message)

    del message['name_1']
    del message['name_2']

    return bits.to_nmea()


ais19_fields = Struct(
    Uint(name='id', nbits=6, default=18),
    Uint(name='repeat_indicator', nbits=2, default=0),
    Uint(name='mmsi', nbits=30),
    Uint(name='spare', nbits=8, default=0),
    Uint10(name='sog', nbits=10, default=102.3),
    Uint(name='position_accuracy', nbits=1, default=0),
    LatLon(name='x', nbits=28, default=181),
    LatLon(name='y', nbits=27, default=91),
    Uint10(name='cog', nbits=12, default=360),
    Uint(name='true_heading', nbits=9, default=511),
    Uint(name='timestamp', nbits=6, default=60),
    Uint(name='spare2', nbits=4, default=0),
    ASCII6(name='name_1', nbits=60),
    ASCII6(name='name_2', nbits=60),
    Uint(name='type_and_cargo', nbits=8, default=0),
    Uint(name='dim_a', nbits=9, default=0),
    Uint(name='dim_b', nbits=9, default=0),
    Uint(name='dim_c', nbits=6, default=0),
    Uint(name='dim_d', nbits=6, default=0),
    Uint(name='fix_type', nbits=4, default=0),
    Bool(name='raim', nbits=1, default=0),
    Uint(name='dte', nbits=1, default=0),
    Bool(name='assigned_mode', nbits=1, default=0),
    Uint(name='spare3', nbits=4, default=0)
)
