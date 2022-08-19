"""
Tools for transcoding from an bitstring to dict according to an arbitrary mapping
"""

import bitstring
from bitstring import ConstBitStream as Bits
from abc import ABC
from abc import abstractmethod

from ais import DecodeError


AIS6toASCII8 = [chr(i+48) for i in range(40)] + [chr(i+96) for i in range(24)]
ASCII8toAIS6 = {c: i for i, c in enumerate(AIS6toASCII8)}
ASCII6toASCII8 = [c for c in "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_ !\"#$%&`()*+,-./0123456789:;<=>?"]
ASCII8toASCII6 = {c: i for i, c in enumerate(ASCII6toASCII8)}


def byte_align(bits):
    pad = 8 - (len(bits) % 8)
    if pad < 8:
        bits += Bits(uint=0, length=pad)
    return bits


def bits_to_nmea(bits):
    pad = 6 - (len(bits) % 6)
    if pad == 6:
        pad = 0
    else:
        bits += Bits(uint=0, length=pad)
    body = ''.join([AIS6toASCII8[b.uint] for b in bits.cut(6)])
    return body, pad


def nmea_to_bits(body, pad):
    bits = Bits()
    for c in body:
        bits += Bits(uint=ASCII8toAIS6[c], length=6)
    if pad:
        bits = bits[:0-pad]
    return bits


class Transcoder(ABC):
    @abstractmethod
    def encode(self, message):
        raise NotImplementedError

    @abstractmethod
    def decode(self, bits, message=None):
        raise NotImplementedError


class MessageTranscoder(Transcoder):
    """
    Transcode a list of fields
    """
    def __init__(self, fields=None):
        self._fields = fields or []

    def get_fields(self, message=None):
        return self._fields

    def encode_fields(self, message):
        return self.get_fields(message)

    def decode_fields(self, bits, message):
        return self.get_fields(message)

    def encode(self, message):
        bits = Bits()
        for f in self.encode_fields(message):
            bits += f.encode(message)
        return bits

    def decode(self, bits, message=None):
        message = message or {}
        for f in self.decode_fields(bits, message):
            message.update(f.decode(bits, message))
        return message


class FieldTranscoder(Transcoder):
    """
    Transcode a single value in a single field
    """

    default_value = 0

    def __init__(self, name, nbits, default=None):
        self.name = name
        self._nbits = nbits
        self.default = default if default is not None else self.default_value

    @property
    def nbits(self):
        return self._nbits

    def read_bits(self, bits):
        try:
            return bits.read(self.nbits)
        except bitstring.ReadError as e:
            raise DecodeError('{} {}'.format(self.__class__.__name__, str(e)))

    def encode(self, message):
        value = message.get(self.name, self.default)
        return self.encode_value(value)

    def decode(self, bits, message=None):
        value = self.decode_value(self.read_bits(bits))
        return {self.name: value}

    @abstractmethod
    def encode_value(self, value):
        raise NotImplementedError

    @abstractmethod
    def decode_value(self, bits):
        raise NotImplementedError


class BitsTranscoder(FieldTranscoder):
    def encode_value(self, value):
        bits = Bits(bin=value)
        assert len(bits) == self.nbits
        return bits

    def decode_value(self, bits):
        return bits.bin


class HexTranscoder(FieldTranscoder):
    def encode_value(self, value):
        bits = Bits(hex=value)
        print(bits, len(bits), self.nbits)
        assert len(bits) == self.nbits
        return bits

    def decode_value(self, bits):
        return bits.hex


class VariableLengthHexTranscoder(HexTranscoder):
    def __init__(self, name, default=None):
        super().__init__(name, nbits=0, default=default)

    def read_bits(self, bits):
        # read all the remaining bits
        nbits = len(bits) - bits.pos
        try:
            return bits.read(nbits)
        except bitstring.ReadError as e:
            raise DecodeError('{} {}'.format(self.__class__.__name__, str(e)))

    def encode_value(self, value):
        bits = Bits()
        try:
            bits = Bits(hex=value)
        except KeyError:
            raise DecodeError('{} invalid Hexadecimal string "{}"'.format(self.__class__.__name__, value))
        return bits


class IntTranscoder(FieldTranscoder):
    def encode_value(self, value):
        return Bits(int=value, length=self.nbits)

    def decode_value(self, bits):
        return bits.int


class UintTranscoder(FieldTranscoder):
    def encode_value(self, value):
        return Bits(uint=value, length=self.nbits)

    def decode_value(self, bits):
        return bits.uint


class BooleanTranscoder(FieldTranscoder):
    def __init__(self, name, nbits=1, default=None):
        assert (nbits == 1)
        super().__init__(name, nbits, default)

    def encode_value(self, value):
        return Bits(bool=value)

    def decode_value(self, bits):
        return bits.bool


class ASCII6Transcoder(FieldTranscoder):
    default_value = ''

    def encode_value(self, value):
        bits = Bits()
        for c in value:
            try:
                bits += Bits(uint=ASCII8toASCII6[c], length=6)
            except KeyError:
                raise DecodeError('{} invalid ASCII6 character "{}"'.format(self.__class__.__name__, c))
        if len(bits) < self.nbits:
            bits += Bits(uint=0, length=self.nbits - len(bits))
        return bits

    def decode_value(self, bits):
        return ''.join([ASCII6toASCII8[b.uint] for b in bits.cut(6)])


class VariableLengthASCII6Transcoder(ASCII6Transcoder):
    def __init__(self, name, default=None):
        super().__init__(name, nbits=0, default=default)

    def read_bits(self, bits):
        # read all the remaining bits in chunks of 6
        nbits = (len(bits) - bits.pos) // 6 * 6
        try:
            return bits.read(nbits)
        except bitstring.ReadError as e:
            raise DecodeError('{} {}'.format(self.__class__.__name__, str(e)))

    def encode_value(self, value):
        bits = Bits()
        for c in value:
            try:
                bits += Bits(uint=ASCII8toASCII6[c], length=6)
            except KeyError:
                raise DecodeError('{} invalid ASCII6 character "{}"'.format(self.__class__.__name__, c))
        return bits


class Uint10Transcoder(FieldTranscoder):
    def encode_value(self, value):
        return Bits(uint=round(value * 10), length=self.nbits)

    def decode_value(self, bits):
        return bits.uint / 10.0


class LatLonTranscoder(FieldTranscoder):
    def encode_value(self, value):
        return Bits(int=round(value * 600000), length=self.nbits)

    def decode_value(self, bits):
        return round(bits.int / 600000.0, 6)
