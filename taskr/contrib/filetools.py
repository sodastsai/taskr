#
# Copyright 2014-2015 sodastsai
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from __future__ import unicode_literals, division, absolute_import, print_function

import hashlib
import os
import six

if six.PY3:
    import pathlib


def md5(file_or_path, hash_obj=None):
    """
    >>> import os
    >>> import random
    >>> import tempfile
    >>> from taskr.contrib.system import run
    >>> with tempfile.TemporaryDirectory() as tempdir:
    ...     temppath = os.path.join(tempdir, 'test')
    ...     with open(temppath, 'w') as f:
    ...         _1 = f.write(str(random.randint(1, 1024)))  # Suppress output
    ...         _2 = f.write(' ')  # Suppress output
    ...         _3 = f.write(str(random.randint(1, 1024)))  # Suppress output
    ...     expected, _ = run("md5 {} | awk '{{print $4}}'".format(temppath))
    ...     result_path = md5(temppath).hexdigest()
    ...     with open(temppath, 'rb') as f:
    ...         result_file = md5(f).hexdigest()
    ...     expected == result_file == result_path
    True

    :type file_or_path: str|pathlib.Path|io.FileIO|list|tuple
    :type hash_obj: _hashlib.HASH|None
    :rtype: _hashlib.HASH
    """
    hash_obj = hash_obj or hashlib.md5()

    if isinstance(file_or_path, (list, tuple)):
        for _file_or_path in file_or_path:
            md5(_file_or_path, hash_obj)
    elif isinstance(file_or_path, six.string_types):
        _path_str = file_or_path  # type: str
        if os.path.isdir(_path_str):
            for _sub_path_str in (os.path.join(root, file) for root, _, files in os.walk(_path_str) for file in files):
                with open(_sub_path_str, 'rb') as file:
                    _md5_file(file, hash_obj)
        else:
            with open(_path_str, 'rb') as file:
                _md5_file(file, hash_obj)
    elif six.PY3 and isinstance(file_or_path, pathlib.Path):
        _path_obj = file_or_path  # type: pathlib.Path
        if _path_obj.is_dir():
            for _sub_path_obj in _path_obj.glob('**/*'):
                with _sub_path_obj.open('rb') as file:
                    _md5_file(file, hash_obj)
        else:
            with _path_obj.open('rb') as file:
                _md5_file(file, hash_obj)
    else:
        _md5_file(file_or_path, hash_obj)

    return hash_obj


def _md5_file(file, hash_obj):
    """
    :type file: io.FileIO
    :type hash_obj: _hashlib.HASH
    :rtype: _hashlib.HASH
    """
    buffer_length = 128
    _buffer = file.read(buffer_length)
    while len(_buffer) > 0:
        hash_obj.update(_buffer)
        _buffer = file.read(buffer_length)

    return hash_obj


if __name__ == '__main__':
    import sys
    print(md5(sys.argv[1:] or os.getcwd()).hexdigest())
