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

import argparse
import unittest
from collections import OrderedDict

import six

from taskr.taskr import Task, TaskManager
from taskr.parameters import ParameterClass


# noinspection PyUnusedLocal
def run(origin, destination, speed=1, quiet=False, *args, **kwargs):
    return "Run from {} to {}".format(origin, destination)


def fly(origin, destination):
    return "Fly from {} to {}".format(origin, destination)


class TaskCreationTests(unittest.TestCase):

    def setUp(self):
        super(TaskCreationTests, self).setUp()
        self.task_manager = TaskManager()
        self.task = Task(run, self.task_manager)

    def test_callable(self):
        self.assertEqual("Run from Tokyo to Osaka", self.task("Tokyo", "Osaka"))

    def test_name(self):
        self.assertEqual("run", self.task.name)

    def test_string(self):
        self.assertEqual("run", six.text_type(self.task))
        self.assertEqual("<Task run>", "{!r}".format(self.task))

    def test_raw_parameters(self):
        raw_parameters = list(self.task.raw_parameters.values())
        self.assertEqual(6, len(raw_parameters))
        self.assertTrue(self.task.has_var_keyword)

        self.assertEqual("origin", raw_parameters[0].name)
        self.assertEqual(ParameterClass.POSITIONAL_OR_KEYWORD, raw_parameters[0].kind)
        self.assertEqual(ParameterClass.empty, raw_parameters[0].default)

        self.assertEqual("destination", raw_parameters[1].name)
        self.assertEqual(ParameterClass.POSITIONAL_OR_KEYWORD, raw_parameters[1].kind)
        self.assertEqual(ParameterClass.empty, raw_parameters[1].default)

        self.assertEqual("speed", raw_parameters[2].name)
        self.assertEqual(ParameterClass.POSITIONAL_OR_KEYWORD, raw_parameters[2].kind)
        self.assertEqual(1, raw_parameters[2].default)

        self.assertEqual("quiet", raw_parameters[3].name)
        self.assertEqual(ParameterClass.POSITIONAL_OR_KEYWORD, raw_parameters[3].kind)
        self.assertEqual(False, raw_parameters[3].default)

        self.assertEqual("args", raw_parameters[4].name)
        self.assertEqual(ParameterClass.VAR_POSITIONAL, raw_parameters[4].kind)
        self.assertEqual(ParameterClass.empty, raw_parameters[4].default)

        self.assertEqual("kwargs", raw_parameters[5].name)
        self.assertEqual(ParameterClass.VAR_KEYWORD, raw_parameters[5].kind)
        self.assertEqual(ParameterClass.empty, raw_parameters[5].default)


class TaskSetArgumentTests(unittest.TestCase):

    def setUp(self):
        super(TaskSetArgumentTests, self).setUp()
        self.task_manager = TaskManager()
        self.task = Task(run, self.task_manager)

    def test_set_argument(self):
        self.task.set_group_argument("group1", "name", action="store_true")
        self.task.set_group_argument("group2", "--value", nargs="?")
        self.task.set_group_argument("group2", "age", dest="year")
        self.task.set_argument("--yo", dest="XD", action="store_false")
        self.task.set_group_argument("location", "origin", default="Tokyo")
        self.assertEqual(OrderedDict((
            ("origin", ("location", ("origin",), {"default": "Tokyo"})),
            ("destination", ("*", ("destination",), {"type": six.text_type})),
            ("speed", ("*", ("-s", "--speed",), {"type": int, "default": 1, "required": False})),
            ("quiet", ("*", ("-q", "--quiet",), {"action": "store_true", "default": False, "required": False})),
            ("args", ("*", ("args",), {"nargs": argparse.REMAINDER})),
            ("name", ("group1", ("name",), {"action": "store_true"})),
            ("value", ("group2", ("--value",), {"nargs": "?"})),
            ("year", ("group2", ("age",), {"dest": "year"})),
            ("XD", ("*", ("--yo",), {"dest": "XD", "action": "store_false"})),
        )), self.task.registered_arguments)

        task2 = Task(fly, self.task_manager)
        with self.assertRaises(ValueError) as exception_cm:
            task2.set_argument("speed", default=1)
        self.assertEqual("\"speed\" is not allowed to be added as an argument of fly. "
                         "fly doesn't accept extra keyword args.", str(exception_cm.exception))
