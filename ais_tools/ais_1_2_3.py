import ais as libais


def ais_1_2_3_decode(body, pad):
    return libais.decode(body[:28], 0)
