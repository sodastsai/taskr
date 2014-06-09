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

import csv


class CSVReader(object):

    def __init__(self, path, as_dict=True, value_converter=None):
        self._file_path = path
        self._as_dict = as_dict
        self._content = None

        self.value_converter = value_converter or (lambda x, y: y)

    @property
    def file_path(self):
        return self._file_path

    @property
    def as_dict(self):
        return self._as_dict

    def read(self):
        with open(self._file_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            self._content = []
            if self.as_dict:
                header_row = next(csv_reader)
                for line in csv_reader:
                    block = {}
                    for key, value in dict(zip(header_row, line)).items():
                        block[key] = self.value_converter(key, value)
                    self._content.append(block)
            else:
                for line in csv_reader:
                    self._content.append(line)

    @property
    def content(self):
        if self._content is None:
            self.read()
        return self._content
