# ais-tools
Tools for reading and writing AIS messages


## Install
```console
git clone https://github.com/SkyTruth/ais-tools
pip install ais-tools/
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
