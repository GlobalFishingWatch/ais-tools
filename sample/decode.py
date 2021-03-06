import json
from ais_tools.aivdm import AIVDM
from ais_tools.message import Message


nmea = [
    '\\c:1599239526500,s:sdr-experiments,T:2020-09-04 18.12.06*5D\\!AIVDM,1,1,,A,B>cSnNP00FVur7UaC7WQ3wS1jCJJ,0*73',
    '\\c:1599239587658,s:sdr-experiments,T:2020-09-04 18.13.07*58\\!AIVDM,1,1,,B,H>cSnNP@4eEL544000000000000,0*3E',
    '\\c:1599239644720,s:sdr-experiments,T:2020-09-04 18.14.04*5E\\!AIVDM,1,1,,B,H>cSnNTU7B=40058qpmjhh000004,0*31',
]

decoder = AIVDM()

for msg in Message.stream(nmea):
    msg = decoder.decode(msg)
    print(json.dumps(msg))
