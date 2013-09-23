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

# This script takes and FBX,
# converts it into python data then back into an FBX.
# It simply ensures we're not breaking any data
# and provides a fairly simple example of how to use the API.
#
# It doesn't yet validate the output, however reading with other tools
# is a good enough way to test at the moment.

# handle crummy sys.path
import os
import sys

SOURCE_DIR = os.path.normpath(os.path.abspath(os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))))
sys.path.append(SOURCE_DIR)


def fbx_to_py(fn):
    import pyfbx.parse_bin
    fbx_root_elem, fbx_version = pyfbx.parse_bin.parse(fn, use_namedtuple=True)
    py_data = fbx_root_elem, fbx_version
    return py_data


def py_to_fbx(fn, py_data):
    import pyfbx.encode_bin
    from pyfbx.encode_bin import FBXElem
    from pyfbx import data_types

    fbx_root_elem_in, fbx_version_in = py_data

    # re-build data
    def elem_conv_recursive(ele_in, ele_out):
        for i, data in enumerate(ele_in.props):
            data_type = ele_in.props_type[i]

            if data_type == data_types.BOOL:
                ele_out.add_bool(data)
            elif data_type == data_types.INT16:
                ele_out.add_int16(data)
            elif data_type == data_types.INT32:
                ele_out.add_int32(data)
            elif data_type == data_types.INT64:
                ele_out.add_int64(data)
            elif data_type == data_types.FLOAT32:
                ele_out.add_float32(data)
            elif data_type == data_types.FLOAT64:
                ele_out.add_float64(data)
            elif data_type == data_types.BYTES:
                ele_out.add_bytes(data)
            elif data_type == data_types.STRING:
                ele_out.add_string(data)
            elif data_type == data_types.INT32_ARRAY:
                ele_out.add_int32_array(data)
            elif data_type == data_types.INT64_ARRAY:
                ele_out.add_int64_array(data)
            elif data_type == data_types.FLOAT32_ARRAY:
                ele_out.add_float32_array(data)
            elif data_type == data_types.FLOAT64_ARRAY:
                ele_out.add_float64_array(data)
            elif data_type == data_types.BOOL_ARRAY:
                ele_out.add_bool_array(data)
            elif data_type == data_types.BYTE_ARRAY:
                ele_out.add_byte_array(data)
            else:
                raise Exception("Unknown type %r" % data_type)

        for ele_iter_in in ele_in.elems:
            ele_iter_out = FBXElem(ele_iter_in.id)
            elem_conv_recursive(ele_iter_in, ele_iter_out)
            ele_out.elems.append(ele_iter_out)

    fbx_root_elem_out = FBXElem(b'')
    elem_conv_recursive(fbx_root_elem_in, fbx_root_elem_out)

    pyfbx.encode_bin.write(fn, fbx_root_elem_out, fbx_version_in)


def main():
    for arg in sys.argv[1:]:
        fn_in = arg
        fn_out = os.path.splitext(arg)[0] + "_out.fbx"

        py_data = fbx_to_py(fn_in)
        py_to_fbx(fn_out, py_data)

        print("Written: %r" % fn_out)

if __name__ == "__main__":
    main()
