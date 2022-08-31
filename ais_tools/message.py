"""
utilities for manipulating AIS messages as NMEA strings, json strings or dicts
"""

import json
from urllib.parse import quote as url_quote
import posixpath as pp
import uuid


default_uuid_fields = ('source', 'nmea', 'tagblock_timestamp')


class UUID:
    """
    Create a UUID from a set of args
    """

    UUID_URL_BASE = 'ais-tools'

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
                message = message.strip()
                if len(message) == 0:
                    pass
                elif message[0] == '{':
                    # looks like json, try to parse it
                    try:
                        self.update(json.loads(message))
                    except json.JSONDecodeError as e:
                        # Nope - not JSON.  Giving up...
                        self.update(dict(nmea=message, error="JSONDecodeError: {}".format(str(e))))
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

    def create_uuid(self, fields=default_uuid_fields):
        return str(UUID('ais-tools', *[str(self.get(f, '')) for f in fields]))

    def add_uuid(self, overwrite=False, fields=default_uuid_fields):
        if self.get('uuid') is None or overwrite:
            self['uuid'] = self.create_uuid(fields=fields)
        return self

    @classmethod
    def stream(cls, messages):
        for msg in messages:
            yield Message(msg)
