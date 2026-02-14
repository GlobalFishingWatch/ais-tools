![build](https://github.com/GlobalFishingWatch/ais-tools/workflows/Python%20package/badge.svg)
![python](https://img.shields.io/badge/python-3.10+-blue.svg)
[![codecov](https://codecov.io/gh/GlobalFishingWatch/ais-tools/branch/master/graph/badge.svg)](https://codecov.io/gh/GlobalFishingWatch/ais-tools)
[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# ais-tools
Tools for encoding and decoding AIS messages

Uses https://github.com/schwehr/libais as the base decoder

## Multi-sentence messages
The strategy for handing multi-sentence messages, such as AIS type 5, is to group the sentence parts into a single unit as early as possible in the processing chain.  Ideally this happens at the AIS receiver or at the point when these messages are streaming in real-time and the tagblock with timestamp is added to the !AIVDM payload.

This can be done in a text stream by simply concatenating the sentence parts into a single line of text.  In a JSON encoded message, this can also be done by providing a list in the nmea attribute.

For example:

the following two line message
```text
!AIVDM,2,1,1,B,56:`@2h00001`dQP001`PDpMPTs7SH000000001@0000000000<000000000,0*3E
!AIVDM,2,2,1,B,00000000000,2*26
```
becomes
```text
!AIVDM,2,1,1,B,56:`@2h00001`dQP001`PDpMPTs7SH000000001@0000000000<000000000,0*3E!AIVDM,2,2,1,B,00000000000,2*26
```
messages with tagblock are also concatenated including the tagblock so
```text
\tagblock\!AIVDM_part_one
\tagblock\!AIVDM_part_two
```
becomes
```text
\tagblock\!AIVDM_part_one\tagblock\!AIVDM_part_two
```

## Install
```console
$ pip install git+https://github.com/GlobalFishingWatch/ais-tools
```
## Command line usage

```console
$ ais-tools --help
```
### Decode
Decode nmea in a file as json to stdout
```console
$ ais-tools decode ./sample/sample.nmea
```

### Add tagblock
Used to add a tagblock to AIVDM messages. this is intended to be used with 
a real time stream of messages as they are received, for instance from an 
AIS RF signal decoder or from a udp stream.  The default action is to apply 
the current timestamp

```console
$ echo '!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49' | ais-tools add-tagblock -s my-station
```

outputs something like

```console
\\c:1577762601537,s:my-station,T:2019-12-30 22.23.21*5D\\!AIVDM,1,1,,A,15NTES0P00J>tC4@@FOhMgvD0D0M,0*49
```

### Join Multipart
  Match up multipart nmea messages

  Takes a stream of nmea text lines and tries to find the matching parts of
  multi part messages which may not be adjacent in the stream and may come
  out of order.

  Matched message parts will be concatenated together into a single line
  using join_multipart() All other messages will come out with no changes

```console
$ ais-tools join-multipart ./sample/multi-part.nmea > joined.nmea
```

### Chaining operations
To perform multiple operations on a stream of messages, use the pipe operator

```console
$ ais-tools join-multipart ./sample/multi-part.nmea | ais-tools decode > decoded.nmea
```

## Python usage
Decode NMEA
```python
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
```

## Developing

```console
git clone https://github.com/GlobalFishingWatch/ais-tools
cd ais-tools
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
ruff check .
pytest --cov=./
```
