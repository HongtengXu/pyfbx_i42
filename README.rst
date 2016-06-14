pyfbx_i42
=========

Currently this project contains ``pyfbx/parse_bin.py``,
a simple but functional parser for binary FBX data written for Python3,
which can load in the FBX hierarchy.

To create binary FBX files ``pyfbx/encode_bin.py``
a simple module to support writing FBX files.

Neither of these modules contain utility functions for dealing with the data.
(So no special handling of Vector, Color, Matrix types for example).

This script is based on assimp's ``FBXBinaryTokenizer.cpp`` for the parser.


What Works
----------
- tested FBX files from 2006 - 2012.
  *(parsing data seems not to depend on exact versions)*.
- all known datatypes (float/int arrays, loading binary data, strings etc).
- zlib compression.
- parsing and re-encoding and FBX file. See: ``tests/reencode.py``


What Doesn't Work
-----------------
- ASCII FBX.  Currently the only workaround is to use ``fbxconvert`` to get a binary version.
- Encoding currently uses a hard-coded date, FBX-SDK obfuscates the date and we don't
  yet know how to encode/decode the date value,
  so for now the real date is replaced with a constant value.


Examples
--------

Currently there is a simple example script called ``fbx2json.py``
this standalone Python script will write a ``JSON`` file for each ``FBX`` passed,
Even though its intended mainly as an example it may prove useful in some situations.
