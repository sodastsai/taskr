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

import six

from taskr.argparse import ArgumentParser, ArgumentTypeError, DefaultHelpFormatter


class TaskrArgumentParserTests(unittest.TestCase):

    def setUp(self):
        super(TaskrArgumentParserTests, self).setUp()
        self.parser = ArgumentParser()

        self.parser.add_argument("-a", "--answer", default=42, type=int)
        self.parser.add_argument("name")

    def test_creation(self):
        self.assertEqual("resolve", self.parser.conflict_handler)
        self.assertEqual(DefaultHelpFormatter, self.parser.formatter_class)

    def test_with_empty_sys(self):
        original_argv = sys.argv
        sys.argv = ["TaskrArgumentParserTests"]
        with six.assertRaisesRegex(self, ArgumentTypeError, r"^the following arguments are required: name$") as cm:
            self.parser.parse_args()
        self.assertEqual("{}: error: the following arguments are required: name".format(self.parser.prog),
                         repr(cm.exception))
        sys.argv = original_argv

    def test_with_sys_1(self):
        original_argv = sys.argv

        sys.argv = ["TaskrArgumentParserTests", "Peter", "Alice"]
        arguments, remainders = self.parser.parse_args()
        self.assertEqual({"name": "Peter", "answer": 42}, arguments)
        self.assertSequenceEqual(("Alice",), remainders)
        sys.argv = original_argv

    def test_with_sys_2(self):
        original_argv = sys.argv

        sys.argv = ["TaskrArgumentParserTests", "Peter", "--answer", "4242"]
        arguments, remainders = self.parser.parse_args()
        self.assertEqual({"name": "Peter", "answer": 4242}, arguments)
        self.assertSequenceEqual((), remainders)
        sys.argv = original_argv

    def test_with_empty_args(self):
        with six.assertRaisesRegex(self, ArgumentTypeError, r"^the following arguments are required: name$") as cm:
            self.parser.parse_args(args=())
        self.assertEqual("{}: error: the following arguments are required: name".format(self.parser.prog),
                         repr(cm.exception))

    def test_with_args_1(self):
        arguments, remainders = self.parser.parse_args(args=("Peter", "Alice"))
        self.assertEqual({"name": "Peter", "answer": 42}, arguments)
        self.assertSequenceEqual(("Alice",), remainders)

    def test_with_args_2(self):
        arguments, remainders = self.parser.parse_args(args=("Peter", "--answer", "4242"))
        self.assertEqual({"name": "Peter", "answer": 4242}, arguments)
        self.assertSequenceEqual((), remainders)
