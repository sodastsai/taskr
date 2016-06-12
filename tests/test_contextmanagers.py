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

import sys
import unittest

from taskr.contextmanagers.sys import replace_argv, capture_stdio


class ReplaceArgvTests(unittest.TestCase):

    def test_replace(self):
        original_argv = sys.argv
        with self.assertRaises(ValueError), replace_argv((sys.argv[0], "XD", "yo")):
            self.assertEqual((original_argv[0], "XD", "yo"), sys.argv)
            raise ValueError("Test")
        self.assertEqual(original_argv, sys.argv)


class CaptureStdio(unittest.TestCase):

    def test_capture(self):
        with self.assertRaises(ValueError), capture_stdio() as captured_result:
            sys.stdout.write("XD")
            sys.stderr.write("QQ")
            raise ValueError("Test")
        self.assertEqual(sys.__stdout__, sys.stdout)
        self.assertEqual(sys.__stderr__, sys.stderr)
        self.assertEqual("XD", captured_result.captured_stdout)
        self.assertEqual("QQ", captured_result.captured_stderr)
