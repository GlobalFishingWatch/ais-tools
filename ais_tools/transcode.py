"""
Tools for transcoding from an array of bits to dict according to an arbitrary mapping
"""

from bitarray import bitarray
from bitarray import decodetree
from bitarray.util import int2ba
from bitarray.util import hex2ba
from bitarray.util import ba2hex
import cbitstruct as bitstruct
from abc import abstractmethod

from ais import DecodeError


AIS6toASCII8 = [chr(i+48) for i in range(40)] + [chr(i+96) for i in range(24)]
ASCII8toAIS6 = {c: i for i, c in enumerate(AIS6toASCII8)}
ASCII8toAIS6_bits = {c: int2ba(i, length=6) for i, c in enumerate(AIS6toASCII8)}
ASCII8toAIS6_decode_tree = decodetree(ASCII8toAIS6_bits)

ASCII6toASCII8 = [c for c in "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_ !\"#$%&`()*+,-./0123456789:;<=>?"]
ASCII8toASCII6 = {c: i for i, c in enumerate(ASCII6toASCII8)}
ASCII8toASCII6_bits = {c: int2ba(i, length=6) for i, c in enumerate(ASCII6toASCII8)}
ASCII8toASCII6_decode_tree = decodetree(ASCII8toASCII6_bits)


def bits_to_nmea(bits):
    pad = 6 - (len(bits) % 6)
    if pad == 6:
        pad = 0
    else:
        bits = bits + (pad * bitarray('0'))
    return ''.join(bits.decode(ASCII8toAIS6_decode_tree)), pad


def nmea_to_bits(body, pad):
    bits = bitarray()
    bits.encode(ASCII8toAIS6_bits, body)
    if pad > 0:
        bits = bits[:-pad]
    return bits


class NmeaBits:
    def __init__(self, initializer):
        """
           initialized with a integer length in bits or with a bitarray
        """
        if isinstance(initializer, bitarray):
            self.bits = initializer.copy()
        else:
            self.bits = bitarray(initializer)
            self.bits.setall(0)
        self.buffer = memoryview(self.bits)
        self.offset = 0

    @property
    def length(self):
        return len(self.bits)

    @classmethod
    def from_nmea(cls, body, pad):
        bits = bitarray()
        bits.encode(ASCII8toAIS6_bits, body)
        if pad > 0:
            bits = bits[:-pad]
        return cls(bits)

    def to_nmea(self):
        pad = 6 - (self.length % 6)
        if pad == 6:
            pad = 0
            bits = self.bits
        else:
            bits = self.bits + (pad * bitarray('0'))
        return ''.join(bits.decode(ASCII8toAIS6_decode_tree)), pad

    def pack(self, struct, message):
        self.pack_into(struct, self.offset, message)
        self.offset += struct.nbits

    def pack_into(self, struct, offset, message):
        data = struct.defaults.copy()
        data.update(message)
        for f in struct.encoded_fields:
            data[f.name] = f.encode(data[f.name])
        struct.cf.pack_into(self.buffer, offset, data)

    def unpack(self, struct):
        result = self.unpack_from(struct, self.offset)
        self.offset += struct.nbits
        return result

    def unpack_from(self, struct, offset):
        try:
            message = struct.cf.unpack_from(self.buffer, offset=offset)
        except TypeError as e:
            msg = str(e)
            if msg.startswith('unpack() requires a buffer of at least'):
                msg = f'Not enough bits to decode.  Need at least {struct.nbits} bits, got only {self.length - offset}'
            raise DecodeError(msg)

        for f in struct.encoded_fields:
            message[f.name] = f.decode(message[f.name])
        return message


class NmeaStruct:
    def __init__(self, *args):
        self.fields = list(args)
        self.names = [f.name for f in self.fields]
        self.defaults = {f.name: f.default for f in self.fields if f.default is not None}
        self.nbits = sum(f.nbits for f in self.fields)
        self.encoded_fields = [f for f in self.fields if isinstance(f, EncodedField)]
        self.format_str = ''.join([f.format_str for f in self.fields])
        self.cf = bitstruct.CompiledFormatDict(self.format_str, names=self.names)


class NmeaField:
    def __init__(self, name, nbits, default=None):
        self.name = name
        self.nbits = nbits
        self.default = default
        self.format_type = 'u'

    @property
    def format_str(self):
        return f'{self.format_type}{self.nbits}'


class EncodedField(NmeaField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format_type = 'r'

    @abstractmethod
    def encode(self, value):
        raise NotImplementedError

    @abstractmethod
    def decode(self, value):
        raise NotImplementedError


class UintField(NmeaField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LatLonField(EncodedField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format_type = 's'

    def encode(self, value):
        return round(value * 600000)

    def decode(self, value):
        return round(value / 600000.0, 6)


class BoolField(NmeaField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format_type = 'b'


class Uint10Field(EncodedField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format_type = 'u'

    def encode(self, value):
        return round(value * 10)

    def decode(self, value):
        return value / 10


class BitField(EncodedField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format_type = 'r'

    def encode(self, value):
        # value must be a string of bits eg '110011'
        return bitarray(value).tobytes()

    def decode(self, value):
        # value is a byte array
        b = bitarray()
        b.frombytes(value)
        return b[:self.nbits].to01()


class HexField(EncodedField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format_type = 'r'

    def encode(self, value):
        # value is a hex string without the  '0x' prefix
        return hex2ba(value).tobytes()

    def decode(self, value):
        # value is a bytearray
        b = bitarray()
        b.frombytes(value)
        return ba2hex(b[:self.nbits])


class ASCII6Field(EncodedField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.format_type = 'r'

    def encode(self, value):
        # value is an ascii8 string.  Need to convert to ascii6 and then to bytes
        bits = bitarray()
        bits.encode(ASCII8toASCII6_bits, value)
        return bits.tobytes()

    def decode(self, value):
        # value is raw bytes.  Need to convert 6-bit fields to ascii6 and then to ascii8
        bits = bitarray()
        bits.frombytes(value)
        bits = bits[:self.nbits]
        return ''.join(bits.decode(ASCII8toASCII6_decode_tree))
