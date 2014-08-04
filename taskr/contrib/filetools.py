#
# Copyright 2014 sodastsai
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

import hashlib

def md5(file_path):
    _md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        buffer_length = 128
        _buffer = f.read(buffer_length)
        while len(_buffer) > 0:
            _md5.update(_buffer)
            _buffer = f.read(buffer_length)
    return _md5
