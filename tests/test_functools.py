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

from taskr.funcools import partialmethod


class PartialMethodTestCase(unittest.TestCase):

    def test_partialmethod(self):

        class Adder(object):

            def __init__(self, base=0):
                self.base = base

            def add(self, x, y):
                return self.base + x + y

            add_2 = partialmethod(add, 2)

        adder = Adder()
        # noinspection PyCallingNonCallable
        self.assertEqual(5, adder.add_2(3))
