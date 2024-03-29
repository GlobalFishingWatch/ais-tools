from ais_tools.transcode import NmeaBits
from ais_tools.transcode import NmeaStruct as Struct
from ais_tools.transcode import UintField as Uint
from ais_tools.transcode import Uint10Field as Uint10
from ais_tools.transcode import LatLonField as LatLon
from ais_tools.transcode import BoolField as Bool
from ais_tools.ais_commstate import ais_commstate_decode
from ais_tools.ais_commstate import ais_commstate_encode
from ais_tools.ais_commstate import ais_commstate_CS


def ais18_decode(body, pad):
    bits = NmeaBits.from_nmea(body, pad)
    message = bits.unpack(ais18_fields)

    ais_commstate_decode(bits, message)

    return message


def ais18_encode(message):
    bits = NmeaBits(ais18_fields.nbits + ais_commstate_CS.nbits)
    bits.pack(ais18_fields, message)

    ais_commstate_encode(bits, message)

    return bits.to_nmea()


ais18_fields = Struct(
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
    Uint(name='spare2', nbits=2, default=0),
    Uint(name='unit_flag', nbits=1, default=0),
    Uint(name='display_flag', nbits=1, default=0),
    Uint(name='dsc_flag', nbits=1, default=0),
    Uint(name='band_flag', nbits=1, default=0),
    Uint(name='m22_flag', nbits=1, default=0),
    Bool(name='assigned_mode', nbits=1, default=0),  # NB: Libais calls this 'mode_flag" for type 18, and calls it
                                                     # 'assigned_mode' for 19 and 21.
    Bool(name='raim', nbits=1, default=0),
    Uint(name='commstate_flag', nbits=1, default=0)
)
