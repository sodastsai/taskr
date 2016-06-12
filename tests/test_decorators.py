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

from taskr.decorators.once import once, oncemethod


class OnceTests(unittest.TestCase):

    def test_once_function(self):
        @once()
        def answer():
            if not hasattr(answer, "call_count"):
                answer.call_count = 0
            answer.call_count += 1
            return 42

        answer()
        self.assertEqual(42, answer())
        self.assertEqual(1, answer.call_count)

    def test_once_method(self):

        class Person(object):
            def __init__(self):
                super(Person, self).__init__()
                self.answer_call_count = 0

            @oncemethod()
            def answer(self):
                self.answer_call_count += 1
                return 42

            @oncemethod("_yo")
            def yo(self):
                return "yo"

        person1 = Person()
        person2 = Person()

        self.assertEqual(42, person1.answer())
        self.assertEqual(1, person1.answer_call_count)
        self.assertEqual(42, person2.answer())
        self.assertEqual(1, person2.answer_call_count)

        self.assertEqual("yo", person1.yo())
        # noinspection PyUnresolvedReferences
        self.assertEqual("yo", person1._yo)
