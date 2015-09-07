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
import six


def md5(file_or_path):
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

    :type file_or_path: io.FileIO|str
    :rtype: _hashlib.HASH
    """

    if isinstance(file_or_path, six.string_types):
        with open(file_or_path, 'rb') as file:
            return md5(file)

    file = file_or_path
    """:type: io.FileIO"""

    _md5 = hashlib.md5()
    buffer_length = 128
    _buffer = file.read(buffer_length)
    while len(_buffer) > 0:
        _md5.update(_buffer)
        _buffer = file.read(buffer_length)

    return _md5
