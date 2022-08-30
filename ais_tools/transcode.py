"""
Tools for transcoding from an bitstring to dict according to an arbitrary mapping
"""

from bitarray import bitarray
from bitarray import decodetree
from bitarray.util import int2ba
from bitarray.util import hex2ba
from bitarray.util import ba2hex
import cbitstruct as bitstruct
import bitstring
from bitstring import ConstBitStream as Bits
from abc import ABC
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
    bits = bitarray()
    bits.encode(ASCII8toAIS6_bits, body)
    return Bits(bytes=bits.tobytes(), length=len(body) * 6 - pad)


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
        return ''.join(bits.iterdecode(ASCII8toAIS6_decode_tree)), pad

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
        message = struct.cf.unpack_from(self.buffer, offset=offset)
        for f in struct.encoded_fields:
            message[f.name] = f.decode(message[f.name])
        return message

    # def pack_bytes(self, data):
    #     fmt_str = f'r{len(data) * 8}'
    #     bitstruct.pack_into(fmt_str, self.buffer, self.offset, data)
    #
    # def unpack_bytes(self):
    #     fmt_str = f'r{self.length - self.offset}'
    #     print (fmt_str)
    #     bitarray
    #     bitstruct.unpack_from(fmt_str, self.buffer, self.offset)


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
        return ''.join(bits.iterdecode(ASCII8toASCII6_decode_tree))





# class _FieldTranscoder(Transcoder):
#     """
#     Transcode a single value in a single field
#     """
#
#     default_value = 0
#
#     def __init__(self, name, nbits, default=None):
#         self.name = name
#         self._nbits = nbits
#         self.default = default if default is not None else self.default_value
#         self.format = bitstruct.compile(self.format_str())
#
#     @property
#     def nbits(self):
#         return self._nbits
#
#     def format_str(self):
#         return f'u{self.nbits}'
#
#     def read_bits(self, bits, offset=0):
#         return self.format.unpack_from(bits, offset)
#
#     # def read_bits(self, bits):
#     #     try:
#     #         return bits.read(self.nbits)
#     #     except bitstring.ReadError as e:
#     #         raise DecodeError('{} {}'.format(self.__class__.__name__, str(e)))
#
#     def encode(self, message):
#         value = message.get(self.name, self.default)
#         return self.encode_value(value)
#
#     def decode(self, bits, offset=0, message=None):
#         value = self.decode_value(self.read_bits(bits, offset))
#         return {self.name: value}
#
#     @abstractmethod
#     def encode_value(self, value):
#         raise NotImplementedError
#
#     @abstractmethod
#     def decode_value(self, unpacked_bits):
#         raise NotImplementedError
#
# class _UintTranscoder(FieldTranscoder):
#     def encode_value(self, value, bits, offset):
#         self.format.pack_into(bits, offset, value)
#
#         # return Bits(uint=value, length=self.nbits)
#
#     def decode_value(self, unpacked_bits):
#         return unpacked_bits
#
#
#
# class _StructTranscoder(FieldTranscoder):
#     def __init__(self, fields=None):
#         self._fields = fields or []
#         self.format_str = ''.join([f.format_str] for f in self._fields)
#         self.format = bitstruct.compile(self.format_str)
#
#     def encode_value(self, value):
#         pass
#
#     def decode_value(self, bits):
#
#         pass