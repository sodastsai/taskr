#
# Copyright 2014-2016 Tien-Che Tsai
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

import unittest

from taskr.utils import function_args_count


class UtilsTests(unittest.TestCase):
    def test_function_args_count(self):
        class SomeObject(object):
            def yo(self, task):
                pass

            def hi(self, task, name):
                pass

            def hello(self, task, *args, **kwargs):
                pass

            def hey(self, task, *args):
                pass

            def ciao(self, task, **kwargs):
                pass

        self.assertEqual(function_args_count(SomeObject.yo), 2)
        self.assertEqual(function_args_count(SomeObject.hi), 3)
        self.assertEqual(function_args_count(SomeObject.hello), 4)
        self.assertEqual(function_args_count(SomeObject.hey), 3)
        self.assertEqual(function_args_count(SomeObject.ciao), 3)
