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
from __future__ import unicode_literals, print_function, absolute_import, division
import plistlib
import six


class Plist(object):

    def __init__(self, file_path, mode=None):
        self.file_path = file_path
        self.content_dict = {}
        self.mode = mode or 'r'

    def __getitem__(self, key):
        if key in self.content_dict:
            return self.content_dict[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        self.content_dict[key] = value

    def __delitem__(self, key):
        self.content_dict.pop(key, None)

    def __enter__(self):
        if 'r' in self.mode:
            with open(self.file_path, 'rb') as f:
                self.content_dict = plistlib.load(f) if six.PY3 else plistlib.readPlist(f)
        return self

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_val, exc_tb):
        if 'w' in self.mode:
            with open(self.file_path, 'wb') as f:
                if six.PY3:
                    plistlib.dump(self.content_dict, f)
                else:
                    plistlib.writePlist(self.content_dict, f)
