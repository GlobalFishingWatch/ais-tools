import ais as libais
from ais import DecodeError


def ais5_decode(body, pad):
    try:
        # NB: we ignore any extra bits in the body, so we only take the first 71 characters
        # because libais will raise an exception if the body with pad is not exactly 424 bits.
        # 6 bits per character less the 2 padding bits (71 * 6 - 2 = 424)
        return libais.decode(body[:71], 2)
    except DecodeError as e:
        raise DecodeError(f'TYPE 5 LIBAIS ERR: {str(e)}')

