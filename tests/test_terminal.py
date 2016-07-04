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

from unittest import TestCase

from taskr.terminal import ANSIEscapeCode, ANSIEscapedString


class ANSIEscapeCodeTests(TestCase):

    def test_to_string(self):
        self.assertEqual("\033[31m", ANSIEscapeCode.to_string(ANSIEscapeCode.fRed))
        self.assertEqual("\033[31;1m", ANSIEscapeCode.to_string(ANSIEscapeCode.fRed, ANSIEscapeCode.light))
        self.assertEqual("\033[43;31;1m", ANSIEscapeCode.to_string(ANSIEscapeCode.bYellow,
                                                                   ANSIEscapeCode.fRed,
                                                                   ANSIEscapeCode.light))

    def test_ansi_escaped_string(self):
        hello = ANSIEscapedString("hello", ANSIEscapeCode.light, ANSIEscapeCode.bYellow, ANSIEscapeCode.fRed)
        self.assertEqual("\033[1;43;31mhello\033[0m", str(hello))

    def test_from_string_normal_string(self):
        escaped_string = ANSIEscapedString.from_string("XD")
        self.assertEqual("XD", escaped_string.string)
        self.assertSequenceEqual((), escaped_string.codes)

    def test_from_string(self):
        escaped_string = ANSIEscapedString.from_string("\033[1;31mYo\033[m")
        self.assertEqual("Yo", escaped_string.string)
        self.assertSequenceEqual((ANSIEscapeCode.light, ANSIEscapeCode.fRed), escaped_string.codes)

    def test_strip(self):
        self.assertEqual("XD", ANSIEscapedString.strip("XD"))
        self.assertEqual("Yo", ANSIEscapedString.strip("\033[32mYo\033[m"))
