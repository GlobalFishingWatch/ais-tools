"""
utilities for manipulating AIS messages as NMEA strings, json strings or dicts
"""

import json
import itertools as it
from urllib.parse import quote as url_quote
import posixpath as pp
import uuid


class GFW_UUID:
    """
    ported from https://github.com/GlobalFishingWatch/pipe-tools
    """

    UUID_URL_BASE = '//globalfishingwatch.org'
    SOURCE = 'source'

    def __init__(self, *args):
        self.uuid = self.create_uuid(*args)

    def __str__(self):
        return str(self.uuid)

    # Create a uuid using the given string(s) which are assembled into a url using UUID_URL_BASE
    @classmethod
    def create_uuid(cls, *args):
        args = list(map(url_quote, args))
        return uuid.uuid5(uuid.NAMESPACE_URL, pp.join(cls.UUID_URL_BASE, *args).lower())


class Message(dict):
    def __init__(self, *args, **kwargs):
        if 'nmea' not in kwargs:
            kwargs['nmea'] = ''
        super().__init__(**kwargs)
        if len(args) > 1:
            raise ValueError('Message can only be constructed with a single positional argument or one or more kwargs')
        elif len(args) == 1:
            message = args[0]
            if not message:
                pass
            elif isinstance(message, dict):
                self.update(message)
            elif isinstance(message, str):
                if message[0] == '{':
                    # looks like json, try to parse it
                    self.update(json.loads(message))
                else:
                    # assume it's an NMEA string and pack it up in a dict
                    self.update(dict(nmea=message))
            else:
                raise ValueError("Unable to convert {} to NMEA message".format(message))

    @property
    def nmea(self):
        return self.get('nmea', '')

    def add_source(self, source, overwrite=False):
        if self.get('source') is None or overwrite:
            self['source'] = source
        return self

    def create_uuid(self):
        """
        using this the same way as in https://github.com/GlobalFishingWatch/pipe-orbcomm so it should
        generate the same uuid given the same NMEA string and source='orbcomm'
        """
        return str(GFW_UUID(GFW_UUID.SOURCE, self.get('source', ''), self.get('nmea', '')))

    def add_uuid(self, overwrite=False):
        if self.get('uuid') is None or overwrite:
            self['uuid'] = self.create_uuid()
        return self

    @classmethod
    def stream(cls, messages):
        for msg in messages:
            yield Message(msg)


# def as_dict(message):
#     if not message:
#         return dict(nmea='')
#     elif isinstance(message, dict):
#         return message
#     elif isinstance(message, str):
#         if message[0] == '{':
#             # looks like json, try to parse it
#             return json.loads(message)
#         else:
#             # assume it's an NMEA string and pack it up in a dict
#             return dict(nmea=message)
#     else:
#         raise ValueError("Unable to convert {} to NMEA message".format(message))



# def as_dict_stream(messages):
#     for m in map(as_dict, messages):
#         yield m


# def add_source(message, source, overwrite=False):
#     if message.get('source') is None or overwrite:
#         message['source'] = source
#     return message
#
#
# def add_source_stream(messages, source, overwrite=False):
#     for m in map(add_source, messages, it.repeat(source), it.repeat(overwrite)):
#         yield m
#
#
# def message_uuid(message):
#     """
#     using this the same way as in https://github.com/GlobalFishingWatch/pipe-orbcomm so it should
#     generate the same uuid given the same NMEA string and source='orbcomm'
#     """
#     return str(GFW_UUID(GFW_UUID.SOURCE, message.get('source', ''), message.get('nmea', '')))
#
#
# def _add_uuid(message, overwrite=False):
#     if message.get('uuid') is None or overwrite:
#         message['uuid'] = message_uuid(message)
#     return message
#
#
# def add_uuid_stream(messages, overwrite=False):
#     for m in map(_add_uuid, messages, it.repeat(overwrite)):
#         yield m
#
#
# def as_message(message, source=None, add_uuid=False, overwrite=False):
#     message = as_dict(message)
#     if source:
#         message = add_source(message, source, overwrite)
#     if add_uuid:
#         message = _add_uuid(message, overwrite)
#     return message
#
#
# def message_stream(messages, source=None, add_uuid=False, overwrite=False):
#     for m in map(as_message, messages, it.repeat(source), it.repeat(add_uuid), it.repeat(overwrite)):
#         yield m
