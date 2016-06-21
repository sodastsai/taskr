#
# Copyright 2014-2016 sodastsai
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

from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from taskr.contrib.collections import to_string


class CollectionsTests(TestCase):

    def test_to_string(self):
        self.assertEqual("",
                         to_string([]))
        self.assertEqual("1 and 2",
                         to_string([1, 2]))
        self.assertEqual("1, 2, and 3",
                         to_string([1, 2, 3]))
        self.assertEqual("1, 2, 3, and 5",
                         to_string([1, 2, 3, 5]))
        self.assertEqual("1, 2, 3, and 1 item",
                         to_string([1, 2, 3, 5], threshold=3))
        self.assertEqual("1, 2, 3, and 1 number",
                         to_string([1, 2, 3, 5], threshold=3, item="number", item_plural="numbers"))
        self.assertEqual("1, 2, and 4 items",
                         to_string([1, 2, 3, 5, 6, 7], threshold=2))
        self.assertEqual("1, 2, 3, 5, and 2 numbers",
                         to_string([1, 2, 3, 5, 6, 7], threshold=4, item="number", item_plural="numbers"))
        self.assertEqual("1, 2, 3, 5, 6, and 7",
                         to_string([1, 2, 3, 5, 6, 7], threshold=20))
        self.assertEqual("1, 2, 3, 5, 6, and 7",
                         to_string([1, 2, 3, 5, 6, 7], threshold=-30))
