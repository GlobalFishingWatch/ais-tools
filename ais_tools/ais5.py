import ais as libais
from ais import DecodeError


def ais5_decode(body, pad):
    try:
        # NB: ignore any extra bits in the body if there is a single extra character or extra padding bts.
        # This is based on observations that there are many type 5 messages occurring in the wild that have
        # a pad value of '0' and/or a single extra character, but appear to be valid messages.
        # We take the first 71 characters because libais will raise an exception if the body with pad
        # is not exactly 424 bits.
        # 6 bits per character less the 2 padding bits (71 * 6 - 2 = 424)

        if (71 <= len(body) <= 72):
            body = body[:71]
        return libais.decode(body, 2)
    except DecodeError as e:
        raise DecodeError(f'TYPE 5 LIBAIS ERR: {str(e)}')

