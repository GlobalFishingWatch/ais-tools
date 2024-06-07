import ais as libais
from ais import DecodeError


def ais_1_2_3_decode(body, pad):
    return libais.decode(body[:28], 0)
