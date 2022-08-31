from click.testing import CliRunner

import json
import re

from ais_tools.cli import add_tagblock
from ais_tools.cli import decode
from ais_tools.cli import encode
from ais_tools.cli import join_multipart
from ais_tools.cli import cli
from ais_tools.tagblock import parseTagBlock


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli)
    assert not result.exception
    print(result.output)
    assert result.output.startswith('Usage')


def test_add_tagblock():

    runner = CliRunner()
    input = '!AIVDM,1,1,,A,B>cSnNP00FVur7UaC7WQ3wS1jCJJ,0*73'
    args = '--station=test'
    result = runner.invoke(add_tagblock, input=input, args=args)
    assert not result.exception

    tagblock, nmea = parseTagBlock(result.output.strip())
    assert nmea == input
    assert tagblock['tagblock_station'] == 'test'


def test_decode():
    runner = CliRunner()
    input = '\\c:1599239526500,s:ais-tools,T:2020-09-04 18.12.06*5D\\!AIVDM,1,1,,A,B>cSnNP00FVur7UaC7WQ3wS1jCJJ,0*73'
    result = runner.invoke(decode, input=input)
    assert not result.exception
    msg = json.loads(result.output)
    assert msg['mmsi'] == 985200250


def test_decode_fail():
    runner = CliRunner(mix_stderr=False)
    input = 'INVALID NMEA'
    result = runner.invoke(decode, input=input)
    assert not result.exception
    assert result.stderr.strip() == 'no valid AIVDM message detected'
    msg = json.loads(result.output)
    assert msg['error'] == 'no valid AIVDM message detected'


def test_encode():
    runner = CliRunner()
    input = '{"id":25, "text": "TEST", "mmsi": 123456789}'
    result = runner.invoke(encode, input=input)
    assert not result.exception
    assert result.output.strip() == '!AIVDM,1,1,,A,I1mg=5@0@00:2ab0,5*52'


def test_encode_fail():
    runner = CliRunner(mix_stderr=False)
    input = 'INVALID JSON'
    result = runner.invoke(encode, input=input)
    assert not result.exception
    assert result.stderr.strip() == 'AISTOOLS ERR: Failed to encode unknown message type None'
    assert result.output.strip() == '!AIVDM,1,1,,A,I0000000@002a97a0,5*16'


def test_join_multipart():

    runner = CliRunner()
    nmea = [
        '\\t:1,s:station1*00\\!AIVDM,1,1,1,A,@,0*57',
        '\\t:2.1,g:1-2-001,s:station1*00\\!AIVDM,2,1,1,B,@,0*57',
        '\\t:3,s:station1*00\\!AIVDM,1,1,1,A,@,0*57',
        '\\t:2.2,g:2-2-001,s:station1*00\\!AIVDM,2,2,1,B,@,0*54',
        '\\t:4,s:station1*00\\!AIVDM,1,1,1,A,@,0*57',
        '\\t:5.2*00\\!AIVDM,2,2,5,B,@,0*50',
        '\\t:6,s:station1*00\\!AIVDM,1,1,1,A,@,0*57',
        '\\t:8.2*00\\!AIVDM,2,2,8,A,@,0*5E',
        '\\t:7.1*00\\!AIVDM,2,1,7,B,@,0*51',
        '\\t:5.1*00\\!AIVDM,2,1,5,B,@,0*53',
        '\\t:7.2*00\\!AIVDM,2,2,7,B,@,0*52'
    ]
    args = ''
    result = runner.invoke(join_multipart, input='\n'.join(nmea), args=args)
    assert not result.exception

    actual = [re.findall(r'\\t:([0-9][.]?[0-9]?)', line) for line in result.output.split('\n')]
    actual = [a if len(a) > 1 else a[0] for a in actual if a]
    expected = ['1', '3', ['2.1', '2.2'], '4', '6', ['5.1', '5.2'], ['7.1', '7.2'], '8.2']

    assert expected == actual
