# ais-tools
Tools for reading and writing AIS messages

## Install
```console
pip install git+https://github.com/GlobalFishingWatch/ais-tools
```
## Command line usage

```console
ais_tools --help
```

Decode nmea in a file as json to stdout
```
ais_tools decode ./sample/sample.nmea
```

## Python usage
Decode NMEA
```python
import json
from ais_tools.aivdm import AIVDM


nmea = [
    '\\c:1599239526500,s:sdr-experiments,T:2020-09-04 18.12.06*5D\\!AIVDM,1,1,,A,B>cSnNP00FVur7UaC7WQ3wS1jCJJ,0*73',
    '\\c:1599239587658,s:sdr-experiments,T:2020-09-04 18.13.07*58\\!AIVDM,1,1,,B,H>cSnNP@4eEL544000000000000,0*3E',
    '\\c:1599239644720,s:sdr-experiments,T:2020-09-04 18.14.04*5E\\!AIVDM,1,1,,B,H>cSnNTU7B=40058qpmjhh000004,0*31',
]

decoder = AIVDM()

for msg in decoder.decode_stream(nmea):
    print(json.dumps(msg))
```
## Developing

```console
git clone https://github.com/SkyTruth/ais-tools
cd ais-tools
virtualenv venv
source venv/bin/activate
pip install -e .\[dev\]
pytest
```

## Multi-sentence messages
The strategy for handing multi-sentence messages, such as ASI type 5, is to group the sentence parts into a single unit as early as possible in the processing chain.  Ideally this happens at the AIS receiver or at the point when these messages are streaming in real-time and the tagblock with timestamp is added to the !AIVDM payload.

This can be done in a text stream by simply concatenating the sentence parts into a single line of text.  In a JSON encoded message, this can also be done by providing a list in the nmea attribute.

For example:

[TODO: some type 5 messages here]
