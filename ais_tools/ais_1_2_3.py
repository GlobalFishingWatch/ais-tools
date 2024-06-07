import ais as libais
from ais import DecodeError


def ais_1_2_3_decode(body, pad):
    try:
        return libais.decode(body[:28], 0)
    except DecodeError as e:
        raise DecodeError(f'TYPE 1-2-3 LIBAIS ERR: {str(e)}')

