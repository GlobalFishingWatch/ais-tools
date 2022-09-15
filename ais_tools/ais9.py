from ais_tools.transcode import NmeaBits
from ais_tools.transcode import NmeaStruct as Struct
from ais_tools.transcode import UintField as Uint
from ais_tools.transcode import Uint10Field as Uint10
from ais_tools.transcode import LatLonField as LatLon
from ais_tools.transcode import BoolField as Bool
from ais_tools.ais_commstate import ais_commstate_decode
from ais_tools.ais_commstate import ais_commstate_encode
from ais_tools.ais_commstate import ais_commstate_CS


def ais9_decode(body, pad):
    bits = NmeaBits.from_nmea(body, pad)
    message = bits.unpack(ais9_fields)

    ais_commstate_decode(bits, message)

    return message


def ais9_encode(message):
    bits = NmeaBits(ais9_fields.nbits + ais_commstate_CS.nbits)
    bits.pack(ais9_fields, message)

    ais_commstate_encode(bits, message)

    return bits.to_nmea()


ais9_fields = Struct(
    Uint(name='id', nbits=6, default=18),
    Uint(name='repeat_indicator', nbits=2, default=0),
    Uint(name='mmsi', nbits=30),
    Uint(name='alt', nbits=12, default=4095),
    Uint(name='sog', nbits=10, default=1023),
    Uint(name='position_accuracy', nbits=1, default=0),
    LatLon(name='x', nbits=28, default=181),
    LatLon(name='y', nbits=27, default=91),
    Uint10(name='cog', nbits=12, default=360),
    Uint(name='timestamp', nbits=6, default=60),
    Uint(name='alt_sensor', nbits=1, default=0),
    Uint(name='spare', nbits=7, default=0),
    Uint(name='dte', nbits=1, default=0),
    Uint(name='spare2', nbits=3, default=0),
    Bool(name='assigned_mode', nbits=1, default=0),
    Bool(name='raim', nbits=1, default=0),
    Uint(name='commstate_flag', nbits=1, default=0)
)
