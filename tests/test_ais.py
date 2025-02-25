import pytest
from ais_tools.ais import AISMessageTranscoder
import math

import ais as libais
from ais import DecodeError


@pytest.mark.parametrize("body,pad,ignore", [
    ('B>cSnNP006Vuqd5aC;?Q3wVQjFLr', 0, {'mode_flag'}),
    ('B5O3hLP00H`fAd4naG6E3wR5oP06', 0, {'mode_flag', 'commstate_cs_fill'}),
    ('B6:`hQ@0021M<;T=IQ:FWwR61P06', 0, {'mode_flag', 'commstate_cs_fill'}),
    ('B39J`I0000?Dql7gCSwQ3wWQjE2b', 0, {'mode_flag'}),
    ('B6:k??@0021FQ5SBI0q`GwpSQP06', 0, {'mode_flag'}),
    ('H>cSnNTU7B=40058qpmjhh000004', 0, {'vendor_id', 'spare', 'dim_a', 'dim_b', 'dim_c', 'dim_d'}),
    ('H>cSnNP@4eEL544000000000000', 2, {}),
    ('H>cSnNTU7B=40058qpmjhh000004', 0, {'spare'}),
    ('I0000027FtlE01000VNJ;0`:h`0', 5, {}),
    ('C7m@5n004qtr0wtdVL9GSwrPFK04BL`2L?042@2>B310?1052120', 0, {'assigned_mode'}),
    ('9001?BP=h:qJ9vb;:f7EN1h240Rb', 0, {})
])
def test_nmea_vs_libais(body, pad, ignore):
    is_close_fields = {'x', 'y', 'cog', 'sog'}

    t = AISMessageTranscoder()
    assert t.can_decode(body)
    decoded = t.decode_nmea(body, pad)
    libais_decoded = libais.decode(body, pad)
    assert (body, pad) == t.encode_nmea(decoded)

    expected = {k: v for k, v in libais_decoded.items() if k not in ignore and k not in is_close_fields}
    actual = {k: v for k, v in decoded.items() if k in expected}
    assert expected == actual

    expected = {k: v for k, v in libais_decoded.items() if k in is_close_fields}
    actual = {k: v for k, v in decoded.items() if k in expected}
    for k, v in expected.items():
        assert math.isclose(v, actual[k], rel_tol=0.0000001), \
            'field {} value mismatch libais:{} !~= ais-tools:{}'.format(k, v, actual[k])


@pytest.mark.parametrize("body,expected", [
    ('B6:DE`00AB2303S>IiE2Cwu3QP06', True),
    ('xxx', False),
    ('', False),
])
def test_can_decode(body, expected):
    t = AISMessageTranscoder()
    assert t.can_decode(body) == expected


@pytest.mark.parametrize("message,expected", [
    ({'id': 1}, False),
    ({'id': 18}, True),
    ({'id': 123}, False),
    ({'id': None}, False),
    ({}, False),
])
def test_can_encode(message, expected):
    t = AISMessageTranscoder()
    assert t.can_encode(message) == expected


@pytest.mark.parametrize("body,pad,expected", [
    ('8Nj<9D0000ttt0<D04@<tt<8`H0H@@l44L`<40<@tT`<4T0`=h0', 2,
     {'mmsi': 992151888, 'application_id': '0000',
      'application_data': '0f3cf0031400440cf3c308a18018410d0411ca0c100310f24a0c1240283700'}),
    ('83am8S@j<d8dtfMEuj9loFOM6@00', 0,
     {'application_id': '3232', 'application_data': 'c22cf2e755f72274dd67dd190000'}),
])
def test_ais8(body, pad, expected):
    msg = AISMessageTranscoder.decode_nmea(body, pad)
    actual = {k: v for k, v in msg.items() if k in expected}
    assert actual == expected
    assert AISMessageTranscoder.encode_nmea(msg) == (body, pad)


def test_ais8_wrong_pad():
    body, pad = '83am8S@j<d8dtfMEuj9loFOM6@0', 0   # pad should be 5, not 0
    msg = AISMessageTranscoder.decode_nmea(body, pad)
    assert ('83am8S@j<d8dtfMEuj9loFOM6@0', 2) == AISMessageTranscoder.encode_nmea(msg)


@pytest.mark.parametrize("body,pad,expected", [
    # incorrect padding
    ('56:=31`000008QaF220QD60`T4pN3N2222222216>pN5@50e0ES2@C`6EC`1hCQp8888880', 0,
     {'name': 'HUA JIANG 7         '}),
    # correct padding
    ('56:=31`000008QaF220QD60`T4pN3N2222222216>pN5@50e0ES2@C`6EC`1hCQp8888880', 2,
     {'name': 'HUA JIANG 7         '}),
    # too many bits
    ('538UMb82F1cOD9MOD019E<4@U8000000000000157av:E58k0?SAC2C30@00000000000080', 0,
     {'name': 'RUSADIR@@@@@@@@@@@@@'})
     ])
def test_ais5(body, pad, expected):
    msg = AISMessageTranscoder.decode_nmea(body, pad)
    actual = {k: v for k, v in msg.items() if k in expected}
    assert actual == expected


@pytest.mark.parametrize("body,pad,expected", [
    # not enough bits
    ('56:=31`000008QaF220QD60`T4pN3N2222222216>pN5@50e0ES2@C`6EC`1hCQp888888', 0,
     'TYPE 5 LIBAIS ERR: Ais5: AIS_ERR_BAD_BIT_COUNT'),
])
def test_ais5_fail(body, pad, expected):
    with pytest.raises(DecodeError, match=expected):
        _ = AISMessageTranscoder.decode_nmea(body, pad)


@pytest.mark.parametrize("body,pad,expected", [
    ('9001?BP=h:qJ9vb;:f7EN1h240Rb', 0, {'mmsi': 20298, 'alt': 55, 'sog': 10}),
    ('90009C3dRIM1QSsjSPAa1;h200T4', 0, {'mmsi': 2380, 'alt': 946, 'alt_sensor': 0}),
])
def test_ais9(body, pad, expected):
    msg = AISMessageTranscoder.decode_nmea(body, pad)
    actual = {k: v for k, v in msg.items() if k in expected}
    assert actual == expected
    assert AISMessageTranscoder.encode_nmea(msg) == (body, pad)


@pytest.mark.parametrize("body,pad,expected", [
    ('B:U=ai@09o>61WLb:orRv2010400', 0, {'unit_flag': 0, 'commstate_flag': 0, 'slot_timeout': 1}),
    ('B52T:q@1C6TOpsUj5@??owTQh85G', 0, {'unit_flag': 0, 'commstate_flag': 0, 'slot_timeout': 2}),
    ('B696W<d`0R98PMUHAqvbGwkjh<0=', 0, {'unit_flag': 0, 'commstate_flag': 0, 'slot_timeout': 3}),
    ('B4tOo0000w4o2V9;PIC5cws1l@P1', 0, {'unit_flag': 0, 'commstate_flag': 0, 'slot_timeout': 4}),
    ('B:U8>U@0AG=@4MLddMQraR4P0D00', 0, {'unit_flag': 0, 'commstate_flag': 0, 'slot_timeout': 5}),
    ('B52b:b00:nc34iUbJ;GEowd1hH>b', 0, {'unit_flag': 0, 'commstate_flag': 0, 'slot_timeout': 6}),
    ('B7Oj:n00>bfs5BLHodEaOwW1lL03', 0, {'unit_flag': 0, 'commstate_flag': 0, 'slot_timeout': 7}),
    ('B6:W?VP0027T9d4Ra`kH?wuV1P06', 0, {'unit_flag': 1, 'commstate_flag': 0}),
    ('B39v<;0008<GnW7gF1WQ3wuQnDmJ', 0, {'unit_flag': 0, 'commstate_flag': 1}),
    ('B6:DE`00AB2303S>IiE2Cwu3QP06', 0, {'unit_flag': 0, 'commstate_flag': 0, 'slot_timeout': 0}),
    ('B42OJB@000OKsg5nMAH03wuUkP06', 0, {'unit_flag': 1, 'commstate_flag': 1}),
])
def test_ais18(body, pad, expected):
    msg = AISMessageTranscoder.decode_nmea(body, pad)
    actual = {k: v for k, v in msg.items() if k in expected}
    assert actual == expected
    assert AISMessageTranscoder.encode_nmea(msg) == (body, pad)


@pytest.mark.parametrize("body,pad,expected", [
    ('C8k?R4h06mc;FwrwlfQWpTv0PBL>`2BTNL?WSWKQ1gW:00411R2P', 0, {'name': 'PINGTAIRONG313-0 73%'}),
    ('C8kI2<004V0u6wsPwKH00Qv0PBL>`2BTNL?gkKW1eg:000411R2P', 0, {'assigned_mode': False})
])
def test_ais19(body, pad, expected):
    msg = AISMessageTranscoder.decode_nmea(body, pad)
    actual = {k: v for k, v in msg.items() if k in expected}
    assert actual == expected
    assert AISMessageTranscoder.encode_nmea(msg) == (body, pad)


@pytest.mark.parametrize("fields", [
    {'part_num': 0, 'name': 'ABCDEFGHIJKLMNOP@@@@'},
    {'part_num': 1, 'vendor_id_1371_4': 'GRM'},
    {'part_num': 1, 'mmsi': 987654321, 'mothership_mmsi': 123456789},

])
def test_ais24(fields):
    message = dict(id=24, mmsi=123456789)
    message.update(fields)
    body, pad = AISMessageTranscoder.encode_nmea(message)
    actual = AISMessageTranscoder.decode_nmea(body, pad)
    assert message == {k: v for k, v in actual.items() if k in message}


@pytest.mark.parametrize("body,pad,expected", [
    ('H>cSnNTU7B=40058qpmjhh000004', 0,
     {'vendor_id': 'GRMD@@E', 'vendor_id_1371_4': 'GRM', 'spare': 0, 'vendor_model': 1, 'vendor_serial': 5, 'fix_type': 1}),
    ('H>dR=eTW21DupoUG2ehhhh0@2220', 0,
     {'mmsi': 986222006, 'mothership_mmsi': 4202626}),
])
def test_ais24_part_b(body, pad, expected):
    msg = AISMessageTranscoder.decode_nmea(body, pad)
    assert expected == {k: v for k, v in msg.items() if k in expected}
    assert AISMessageTranscoder.encode_nmea(msg) == (body, pad)


def test_ais24_part_a_incorrect_pad():
    # The correct pad for this message is 2, but sometimes these are found with pad=0
    # libais will complain about the 2 extra bits at the end but we want to
    # just ignore them instead

    body = 'H>cSnNP@4eEL544000000000000'
    pad = 0
    with pytest.raises(DecodeError):
        libais.decode(body, pad)
    actual = AISMessageTranscoder.decode_nmea(body, pad)
    expected = {'name': 'DAKUWAQA@@@@@@@@@@@@'}
    assert expected == {k: v for k, v in actual.items() if k in expected}


@pytest.mark.parametrize("msg", [
    ({'id': 25, 'mmsi': 123456789, 'text': 'SOME TEXT'}),
    ({'id': 25, 'mmsi': 123456789, 'text': 'SOME TEXT', 'addressed': 1, 'dest_mmsi': 123456789}),
])
def test_ais25(msg):
    body, pad = AISMessageTranscoder.encode_nmea(msg)
    print(body, pad)
    actual = AISMessageTranscoder.decode_nmea(body, pad)
    assert msg == {k: v for k, v in actual.items() if k in msg}


def test_ais25_wrong_pad():
    body, pad = 'I8:lin3LSu;r:IN9=F7PGE1lbIFw', 0   # pad should be 5, not 0
    msg = AISMessageTranscoder.decode_nmea(body, pad)
    # trailing pad bits are all 1s in the original, and 0s in the re-encoded result
    assert ('I8:lin3LSu;r:IN9=F7PGE1lbIFP', 5) == AISMessageTranscoder.encode_nmea(msg)


@pytest.mark.parametrize("msg,expected", [
    ({'id': 24, 'mmsi': 123456789, 'part_num': 2}, 'AIS24: unknown part number 2'),
    ({'id': 18, 'mmsi': 123456789, 'slot_timeout': 8}, 'AIS18: unknown slot_timeout value 8'),
])
def test_encode_fail(msg, expected):
    with pytest.raises(DecodeError, match=expected):
        body, pad = AISMessageTranscoder.encode_nmea(msg)


@pytest.mark.parametrize("body,pad,expected", [
    ('H1mg=5H00000000000000000000', 0, 'AIS24: unknown part number 2'),
])
def test_decode_fail(body, pad, expected):
    with pytest.raises(DecodeError, match=expected):
        AISMessageTranscoder.decode_nmea(body, pad)


@pytest.mark.parametrize("body,pad,expected", [
    ('B>qMUb000hhfFpsjH2UDI3v4SP06', 0, False),
    ('B>qHvBP061u2m:2p94AU;wP6cP06', 0, True),
])
def test_type_18_assigned_mode(body, pad, expected):
    msg = AISMessageTranscoder.decode_nmea(body, pad)
    assert msg['assigned_mode'] is expected


@pytest.mark.parametrize("body,expected", [
    ('0', 0), ('w', 63), ('Z', None)
])
def test_bad_message_id(body, expected):
    with pytest.raises(DecodeError, match=f'No decode method available for message type {expected}'):
        AISMessageTranscoder.decode_nmea(body, 0)
