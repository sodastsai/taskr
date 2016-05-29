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

from taskr.utils import ParameterClass, parameters_of_function


class UtilsTests(unittest.TestCase):

    def test_parameters_of_function(self):
        # noinspection PyUnusedLocal
        def run(origin, destination, vehicle, speed=1, cabinet=None, *args, **kwargs): pass

        parameters_dict = parameters_of_function(run)
        parameter_names = list(parameters_dict.keys())
        self.assertListEqual(["origin", "destination", "vehicle", "speed", "cabinet", "args", "kwargs"],
                             parameter_names)

        parameters = list(parameters_of_function(run).values())
        """:type: list[ParameterClass]"""
        self.assertEqual(7, len(parameters))

        self.assertEqual("origin", parameters[0].name)
        self.assertEqual(ParameterClass.POSITIONAL_OR_KEYWORD, parameters[0].kind)
        self.assertEqual(ParameterClass.empty, parameters[0].default)

        self.assertEqual("destination", parameters[1].name)
        self.assertEqual(ParameterClass.POSITIONAL_OR_KEYWORD, parameters[1].kind)
        self.assertEqual(ParameterClass.empty, parameters[1].default)

        self.assertEqual("vehicle", parameters[2].name)
        self.assertEqual(ParameterClass.POSITIONAL_OR_KEYWORD, parameters[2].kind)
        self.assertEqual(ParameterClass.empty, parameters[2].default)

        self.assertEqual("speed", parameters[3].name)
        self.assertEqual(ParameterClass.POSITIONAL_OR_KEYWORD, parameters[3].kind)
        self.assertEqual(1, parameters[3].default)

        self.assertEqual("cabinet", parameters[4].name)
        self.assertEqual(ParameterClass.POSITIONAL_OR_KEYWORD, parameters[4].kind)
        self.assertIsNone(parameters[4].default)

        self.assertEqual("args", parameters[5].name)
        self.assertEqual(ParameterClass.VAR_POSITIONAL, parameters[5].kind)
        self.assertEqual(ParameterClass.empty, parameters[5].default)

        self.assertEqual("kwargs", parameters[6].name)
        self.assertEqual(ParameterClass.VAR_KEYWORD, parameters[6].kind)
        self.assertEqual(ParameterClass.empty, parameters[6].default)

    def test_callable(self):
        class Adder(object):
            def __init__(self, base=0):
                self.value = base

            def __call__(self, value, comment=None):
                self.value += value
                if comment:
                    print(comment)
                return self.value

        adder = Adder()
        parameters = list(parameters_of_function(adder).values())

        self.assertEqual(2, len(parameters))

        self.assertEqual("value", parameters[0].name)
        self.assertEqual(ParameterClass.empty, parameters[0].default)
        self.assertEqual(ParameterClass.POSITIONAL_OR_KEYWORD, parameters[0].kind)

        self.assertEqual("comment", parameters[1].name)
        self.assertIsNone(parameters[1].default)
        self.assertEqual(ParameterClass.POSITIONAL_OR_KEYWORD, parameters[1].kind)
