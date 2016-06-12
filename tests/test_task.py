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

from taskr.task import Task
from taskr.task_manager import TaskManager
from taskr.parameters import ParameterClass


# noinspection PyUnusedLocal
def run(origin, destination, speed=1, quiet=False, **kwargs):
    return "Run from {} to {}".format(origin, destination)


# noinspection PyUnusedLocal
def fly(origin, destination, *args):
    return "Fly from {} to {}".format(origin, destination)


class TaskCreationTests(unittest.TestCase):

    def setUp(self):
        super(TaskCreationTests, self).setUp()
        self.task_manager = TaskManager()
        self.run_task = Task(run, self.task_manager)
        self.fly_task = Task(fly, self.task_manager)

    def test_callable(self):
        self.assertEqual("Run from Tokyo to Osaka", self.run_task("Tokyo", "Osaka"))

    def test_name(self):
        self.assertEqual("run", self.run_task.name)

    def test_string(self):
        self.assertEqual("run", six.text_type(self.run_task))
        self.assertEqual("<Task run>", "{!r}".format(self.run_task))

    def test_run_callable_parameters(self):
        callable_parameters = list(self.run_task.callable_parameters.values())
        self.assertEqual(5, len(callable_parameters))
        self.assertTrue(self.run_task.has_var_keyword)
        self.assertFalse(self.run_task.has_var_positional)

        self.assertEqual("origin", callable_parameters[0].name)
        self.assertEqual(ParameterClass.POSITIONAL_OR_KEYWORD, callable_parameters[0].kind)
        self.assertEqual(ParameterClass.empty, callable_parameters[0].default)

        self.assertEqual("destination", callable_parameters[1].name)
        self.assertEqual(ParameterClass.POSITIONAL_OR_KEYWORD, callable_parameters[1].kind)
        self.assertEqual(ParameterClass.empty, callable_parameters[1].default)

        self.assertEqual("speed", callable_parameters[2].name)
        self.assertEqual(ParameterClass.POSITIONAL_OR_KEYWORD, callable_parameters[2].kind)
        self.assertEqual(1, callable_parameters[2].default)

        self.assertEqual("quiet", callable_parameters[3].name)
        self.assertEqual(ParameterClass.POSITIONAL_OR_KEYWORD, callable_parameters[3].kind)
        self.assertEqual(False, callable_parameters[3].default)

        self.assertEqual("kwargs", callable_parameters[4].name)
        self.assertEqual(ParameterClass.VAR_KEYWORD, callable_parameters[4].kind)
        self.assertEqual(ParameterClass.empty, callable_parameters[4].default)

    def test_fly_callable_parameters(self):
        callable_parameters = list(self.fly_task.callable_parameters.values())
        self.assertEqual(3, len(callable_parameters))
        self.assertFalse(self.fly_task.has_var_keyword)
        self.assertTrue(self.fly_task.has_var_positional)

        self.assertEqual("origin", callable_parameters[0].name)
        self.assertEqual(ParameterClass.POSITIONAL_OR_KEYWORD, callable_parameters[0].kind)
        self.assertEqual(ParameterClass.empty, callable_parameters[0].default)

        self.assertEqual("destination", callable_parameters[1].name)
        self.assertEqual(ParameterClass.POSITIONAL_OR_KEYWORD, callable_parameters[1].kind)
        self.assertEqual(ParameterClass.empty, callable_parameters[1].default)

        self.assertEqual("args", callable_parameters[2].name)
        self.assertEqual(ParameterClass.VAR_POSITIONAL, callable_parameters[2].kind)
        self.assertEqual(ParameterClass.empty, callable_parameters[2].default)


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
        self.task.finalize_argparser()

    def test_finalize_argparser(self):
        task = Task(run, self.task_manager)
        task.set_argument("--answer", default=42)
        task.finalize_argparser()

        self.assertTrue(task._argparser_finalized)
        with self.assertRaises(AssertionError):
            task.set_argument("--year", default=2016)
        with self.assertRaises(AssertionError):
            task.set_group_argument("time", "--year", default=2016)

    def test_setup_argparser(self):
        self.assertEqual(self.task, self.task.parser.get_default("__task__"))

        self.assertSequenceEqual(["origin", "destination"],
                                 [parameter.name for parameter in self.task.positional_parameters])

        actions = OrderedDict(((action.dest, action) for action in self.task.parser._actions))
        """:type: dict[str, argparse.Action]"""
        self.assertEqual(6, len(actions))
        self.assertSequenceEqual(("help", "origin", "destination", "speed", "quiet", "answer"),
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
