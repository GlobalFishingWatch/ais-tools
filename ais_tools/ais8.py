from ais_tools.transcode import UintTranscoder as Uint
from ais_tools.transcode import HexTranscoder as Hex
from ais_tools.transcode import VariableLengthHexTranscoder as VarHex

ais8_fields = [
    Uint(name='id', nbits=6, default=0),
    Uint(name='repeat_indicator', nbits=2),
    Uint(name='mmsi', nbits=30),
    Uint(name='spare', nbits=2),
    Hex(name='application_id', nbits=16),
    VarHex(name='application_data')
]
