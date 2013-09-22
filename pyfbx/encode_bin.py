# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

# Script copyright (C) 2013 Campbell Barton

from . import data_types
from struct import pack
import array
import zlib

_BLOCK_SENTINEL_LENGTH = 13
_BLOCK_SENTINEL_DATA = (b'\0' * _BLOCK_SENTINEL_LENGTH)
_IS_BIG_ENDIAN = (__import__("sys").byteorder != 'little')
_HEAD_MAGIC = b'Kaydara FBX Binary\x20\x20\x00\x1a\x00'


class FBXElem:
    __slots__ = (
        "id",
        "props",
        "props_type",
        "elems",

        "_props_length",  # combine length of props
        "_end_offset",  # byte offset from the start of the file.
        )

    def __init__(self, id):
        assert(len(id) < 256)  # length must fit in a uint8
        self.id = id
        self.props = []
        self.props_type = bytearray()
        self.elems = []
        self._end_offset = -1
        self._props_length = -1

    def add_bool(self, data):
        assert(isinstance(data, bool))
        data = pack('?', data)

        self.props_type.append(data_types.BOOL)
        self.props.append(data)

    def add_int16(self, data):
        assert(isinstance(data, int))
        data = pack('<h', data)

        self.props_type.append(data_types.INT16)
        self.props.append(data)

    def add_int32(self, data):
        assert(isinstance(data, int))
        data = pack('<i', data)

        self.props_type.append(data_types.INT32)
        self.props.append(data)

    def add_int64(self, data):
        assert(isinstance(data, int))
        data = pack('<q', data)

        self.props_type.append(data_types.INT64)
        self.props.append(data)

    def add_float32(self, data):
        assert(isinstance(data, float))
        data = pack('<f', data)

        self.props_type.append(data_types.FLOAT32)
        self.props.append(data)

    def add_float64(self, data):
        assert(isinstance(data, float))
        data = pack('<d', data)

        self.props_type.append(data_types.FLOAT64)
        self.props.append(data)

    def add_bytes(self, data):
        assert(isinstance(data, bytes))
        data = pack('<I', len(data)) + data

        self.props_type.append(data_types.BYTES)
        self.props.append(data)

    def add_string(self, data):
        assert(isinstance(data, bytes))
        data = pack('<I', len(data)) + data

        self.props_type.append(data_types.STRING)
        self.props.append(data)

    def add_string_unicode(self, data):
        assert(isinstance(data, str))
        data = data.decode('utf8')
        data = pack('<I', len(data)) + data

        self.props_type.append(data_types.STRING)
        self.props.append(data)

    def _add_array_helper(self, data, array_type, prop_type, encoding):
        assert(isinstance(data, array.array))
        assert(data.typecode == array_type)

        length = len(data)

        if _IS_BIG_ENDIAN:
            data = data[:]
            data.byteswap()
        data = data.tobytes()

        encoding = 0 if len(data) <= 128 else 1
        if encoding == 0:
            pass
        elif encoding == 1:
            data = zlib.compress(data, 1)

        comp_len = len(data)

        data = pack('<3I', length, encoding, comp_len) + data

        self.props_type.append(prop_type)
        self.props.append(data)

    def add_int32_array(self, data, encoding=0):
        self._add_array_helper(data, 'i', data_types.INT32_ARRAY, encoding)

    def add_int64_array(self, data, encoding=0):
        self._add_array_helper(data, 'q', data_types.INT64_ARRAY, encoding)

    def add_float32_array(self, data, encoding=0):
        self._add_array_helper(data, 'f', data_types.FLOAT32_ARRAY, encoding)

    def add_float64_array(self, data, encoding=0):
        self._add_array_helper(data, 'd', data_types.FLOAT64_ARRAY, encoding)

    def add_bool_array(self, data, encoding=0):
        self._add_array_helper(data, 'b', data_types.BOOL_ARRAY, encoding)

    def add_byte_array(self, data, encoding=0):
        self._add_array_helper(data, 'B', data_types.BYTE_ARRAY, encoding)

    # -------------------------
    # internal helper functions

    def _calc_offsets(self, offset, last):
        """
        Call before writing, calculates fixed offsets.
        """
        assert(self._end_offset == -1)
        assert(self._props_length == -1)

        # print("Offset", offset)
        offset += 12  # 3 uints
        offset += 1 + len(self.id)  # len + idname

        props_length = 0
        for data in self.props:
            # 1 byte for the prop type
            props_length += 1 + len(data)
        self._props_length = props_length
        offset += props_length

        offset = self._calc_offsets_children(offset, last)

        self._end_offset = offset
        return offset

    def _calc_offsets_children(self, offset, last):
        if self.elems:
            for elem in self.elems:
                offset = elem._calc_offsets(offset, elem is self.elems[-1])
            offset += _BLOCK_SENTINEL_LENGTH
        elif not self.props:
            if not last:
                offset += _BLOCK_SENTINEL_LENGTH



        return offset


    def _write(self, write, tell, last):
        assert(self._end_offset != -1)
        assert(self._props_length != -1)

        print(self.id, self._end_offset, len(self.props), self._props_length)
        write(pack('<3I', self._end_offset, len(self.props), self._props_length))

        write(bytes((len(self.id),)))
        write(self.id)

        for i, data in enumerate(self.props):
            write(bytes((self.props_type[i],)))
            write(data)

        self._write_children(write, tell, last)

        if tell() != self._end_offset:
            raise IOError("scope length not reached, "
                          "something is wrong (%d)" % (end_offset - tell()))

    def _write_children(self, write, tell, last):
        if self.elems:
            for elem in self.elems:
                assert(elem.id != b'')
                elem._write(write, tell, elem is self.elems[-1])
            write(_BLOCK_SENTINEL_DATA)
        elif not self.props:
            if not last:
                write(_BLOCK_SENTINEL_DATA)


def write(fn, elem_root, version):
    assert(elem_root.id == b'')

    with open(fn, 'wb') as f:
        write = f.write
        tell = f.tell

        write(_HEAD_MAGIC)
        write(pack('<I', version))

        elem_root._calc_offsets_children(tell(), False)
        elem_root._write_children(write, tell, False)
        write(pack('<I', 0))

        # TODO: footer isn't working at the moment
        write(b'\0' * 32)  # unknown, for alignment?
        write(b'\xFA\xBC\xAB\x0E\xD7\xC1\xDD\x66\xB1\x77\xFA\x83\x1F\xFC\x28\x7B')  # wrong!

        write(b'\0' * 13)  # unknown, for alignment?

        # this is correct (should be 16 bytes aligned though)!
        write(pack('<I', version))
        write(b'\0' * 120)
        write(b'\xf8\x5a\x8c\x6a')  # unknown magic (always the same)!
