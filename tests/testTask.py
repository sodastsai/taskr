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

from taskr.taskr import Task, TaskManager, TaskrHelpFormatter
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


class TaskArgumentParserTests(unittest.TestCase):

    def setUp(self):
        super(TaskArgumentParserTests, self).setUp()
        self.task_manager = TaskManager()
        self.task = Task(run, self.task_manager)
        self.task.set_argument("-a", "--answer", default=42, type=int)
        self.task.setup_argparser()

    def test_setup_argparser(self):
        self.assertEqual(TaskrHelpFormatter, self.task.parser.formatter_class)
        self.assertEqual("resolve", self.task.parser.conflict_handler)
        self.assertEqual(self.task, self.task.parser.get_default("__task__"))

        actions = OrderedDict(((action.dest, action) for action in self.task.parser._actions))
        """:type: dict[str, argparse.Action]"""
        self.assertEqual(7, len(actions))
        self.assertSequenceEqual(("help", "origin", "destination", "speed", "quiet", "args", "answer"),
                                 list(actions.keys()))

        self.assertIsInstance(actions["help"], argparse._HelpAction)
        self.assertSequenceEqual(("-h", "--help"), actions["help"].option_strings)

        self.assertIsInstance(actions["origin"], argparse._StoreAction)
        self.assertEqual(None, actions["origin"].choices)
        self.assertEqual(None, actions["origin"].const)
        self.assertEqual(None, actions["origin"].default)
        self.assertEqual("origin", actions["origin"].dest)
        self.assertEqual(None, actions["origin"].help)
        self.assertEqual(None, actions["origin"].metavar)
        self.assertEqual(None, actions["origin"].nargs)
        self.assertEqual(None, actions["origin"].help)
        self.assertEqual([], actions["origin"].option_strings)
        self.assertEqual(True, actions["origin"].required)
        self.assertEqual(six.text_type, actions["origin"].type)

        self.assertIsInstance(actions["destination"], argparse._StoreAction)
        self.assertEqual(None, actions["destination"].choices)
        self.assertEqual(None, actions["destination"].const)
        self.assertEqual(None, actions["destination"].default)
        self.assertEqual("destination", actions["destination"].dest)
        self.assertEqual(None, actions["destination"].help)
        self.assertEqual(None, actions["destination"].metavar)
        self.assertEqual(None, actions["destination"].nargs)
        self.assertEqual(None, actions["destination"].help)
        self.assertEqual([], actions["destination"].option_strings)
        self.assertEqual(True, actions["destination"].required)
        self.assertEqual(six.text_type, actions["destination"].type)

        self.assertIsInstance(actions["speed"], argparse._StoreAction)
        self.assertEqual(None, actions["speed"].choices)
        self.assertEqual(None, actions["speed"].const)
        self.assertEqual(1, actions["speed"].default)
        self.assertEqual("speed", actions["speed"].dest)
        self.assertEqual(None, actions["speed"].help)
        self.assertEqual(None, actions["speed"].metavar)
        self.assertEqual(None, actions["speed"].nargs)
        self.assertEqual(None, actions["speed"].help)
        self.assertEqual(["-s", "--speed"], actions["speed"].option_strings)
        self.assertEqual(False, actions["speed"].required)
        self.assertEqual(int, actions["speed"].type)

        self.assertIsInstance(actions["quiet"], argparse._StoreTrueAction)
        self.assertEqual(None, actions["quiet"].choices)
        self.assertEqual(True, actions["quiet"].const)
        self.assertEqual(False, actions["quiet"].default)
        self.assertEqual("quiet", actions["quiet"].dest)
        self.assertEqual(None, actions["quiet"].help)
        self.assertEqual(None, actions["quiet"].metavar)
        self.assertEqual(0, actions["quiet"].nargs)
        self.assertEqual(None, actions["quiet"].help)
        self.assertEqual(["-q", "--quiet"], actions["quiet"].option_strings)
        self.assertEqual(False, actions["quiet"].required)
        self.assertEqual(None, actions["quiet"].type)

        self.assertIsInstance(actions["args"], argparse._StoreAction)
        self.assertEqual(None, actions["args"].choices)
        self.assertEqual(None, actions["args"].const)
        self.assertEqual(None, actions["args"].default)
        self.assertEqual("args", actions["args"].dest)
        self.assertEqual(None, actions["args"].help)
        self.assertEqual(None, actions["args"].metavar)
        self.assertEqual(argparse.REMAINDER, actions["args"].nargs)
        self.assertEqual(None, actions["args"].help)
        self.assertEqual([], actions["args"].option_strings)
        self.assertEqual(True, actions["args"].required)
        self.assertEqual(None, actions["args"].type)

        self.assertIsInstance(actions["answer"], argparse._StoreAction)
        self.assertEqual(None, actions["answer"].choices)
        self.assertEqual(None, actions["answer"].const)
        self.assertEqual(42, actions["answer"].default)
        self.assertEqual("answer", actions["answer"].dest)
        self.assertEqual(None, actions["answer"].help)
        self.assertEqual(None, actions["answer"].metavar)
        self.assertEqual(None, actions["answer"].nargs)
        self.assertEqual(None, actions["answer"].help)
        self.assertEqual(["-a", "--answer"], actions["answer"].option_strings)
        self.assertEqual(False, actions["answer"].required)
        self.assertEqual(int, actions["answer"].type)
