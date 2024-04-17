import ais as libais
from ais import DecodeError


def ais5_decode(body, pad):
    try:
        return libais.decode(body, 2)
    except DecodeError as e:
        raise DecodeError(f'TYPE 5 LIBAIS ERR: {str(e)}')

