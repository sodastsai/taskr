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
import sys
import unittest
from collections import OrderedDict

import six

from taskr.argparse import ArgumentTypeError
from taskr.contextmanagers.sys import capture_stdio
from taskr.task import Task
from taskr.task_manager import TaskManager, task_manager_decorator


class TaskManagerTests(unittest.TestCase):

    def setUp(self):
        super(TaskManagerTests, self).setUp()
        self.task_manager = TaskManager()

    def test_string(self):
        @self.task_manager
        def run(): pass

        self.assertEqual("tasks=[run]", six.text_type(self.task_manager))
        self.assertEqual("<TaskManager tasks=[run]>", "{!r}".format(self.task_manager))

    def test_string_with_main(self):
        @self.task_manager
        def run(): pass

        @self.task_manager.main
        def fly(): pass

        self.assertEqual("tasks=[run,fly], main=fly", six.text_type(self.task_manager))
        self.assertEqual("<TaskManager tasks=[run,fly], main=fly>", "{!r}".format(self.task_manager))

    def test_get_or_create_task_object(self):
        def run(): pass

        run_task = self.task_manager.get_or_create_task_object(run)
        self.assertIsInstance(run_task, Task)
        self.assertIn(run_task, self.task_manager)

        run_task2 = self.task_manager.get_or_create_task_object(run_task)
        self.assertIs(run_task, run_task2)

        with self.assertRaises(ValueError) as exception_cm:
            self.task_manager.get_or_create_task_object(1)
        self.assertEqual("1 object is not a callable", str(exception_cm.exception))

    def test_contains(self):
        @self.task_manager
        def run(): pass

        def fly(): pass

        self.assertIn(run, self.task_manager)
        self.assertNotIn(fly, self.task_manager)
        self.assertNotIn("", self.task_manager)

    def test_argparser(self):
        action_subparser = self.task_manager.parser._actions[1]
        self.assertEqual(action_subparser, self.task_manager.task_subparser)
        self.assertIsInstance(action_subparser, argparse._SubParsersAction)

    def test_finalize(self):
        @self.task_manager
        def run(): pass

        @self.task_manager
        def fly(): pass

        self.task_manager.finalize()
        self.assertTrue(self.task_manager._tasks_finalized)
        self.assertTrue(all((task._argparser_finalized for task in self.task_manager.tasks)))
        self.assertTrue(run._argparser_finalized)
        self.assertTrue(fly._argparser_finalized)

    def test_parse(self):
        # noinspection PyUnusedLocal
        @self.task_manager
        @self.task_manager.set_argument("-a", "--answer", default=42, type=int)
        def run(origin, destination, speed=1, **kwargs): pass

        # noinspection PyUnusedLocal
        @self.task_manager
        def fly(origin, destination, *args): pass

        with six.assertRaisesRegex(self, AssertionError, r"^Tasks should be finalized before parsing arguments\.$"):
            self.task_manager.parse(args=())
        self.task_manager.finalize()

        with six.assertRaisesRegex(self, ArgumentTypeError,
                                   r"^cannot find task to execute\. \(choose from 'run', 'fly'\)$" if six.PY3
                                   else r"^too few arguments$"):
            self.task_manager.parse(args=())

        with six.assertRaisesRegex(self, ArgumentTypeError,
                                   r"^the following arguments are required: origin, destination$" if six.PY3
                                   else r"^too few arguments$"):
            self.task_manager.parse(args=("run",))

        with six.assertRaisesRegex(self, ArgumentTypeError,
                                   r"^the following arguments are required: destination$" if six.PY3
                                   else r"^too few arguments$"):
            self.task_manager.parse(args=("run", "tokyo",))

        task, task_args, task_kwargs = self.task_manager.parse(args=("run", "tokyo", "osaka",))
        self.assertEqual(run, task)
        self.assertEqual(("tokyo", "osaka",), task_args)
        self.assertEqual({"speed": 1, "answer": 42}, task_kwargs)

        task, task_args, task_kwargs = self.task_manager.parse(args=("run", "tokyo", "osaka", "-s", "10"))
        self.assertEqual(run, task)
        self.assertEqual(("tokyo", "osaka",), task_args)
        self.assertEqual({"speed": 10, "answer": 42}, task_kwargs)

        task, task_args, task_kwargs = self.task_manager.parse(args=("run", "tokyo", "osaka", "--answer", "4242"))
        self.assertEqual(run, task)
        self.assertEqual(("tokyo", "osaka",), task_args)
        self.assertEqual({"speed": 1, "answer": 4242}, task_kwargs)

        with six.assertRaisesRegex(self, ArgumentTypeError, r"^unrecognized arguments: '56'$"):
            self.task_manager.parse(args=("run", "tokyo", "osaka", "--speed", "100", "56"))

        task, task_args, task_kwargs = self.task_manager.parse(args=("fly", "tokyo", "osaka", "56", "56"))
        self.assertEqual(fly, task)
        self.assertEqual(("tokyo", "osaka", "56", "56"), task_args)
        self.assertEqual({}, task_kwargs)

    def test_dispatch(self):
        @self.task_manager
        @self.task_manager.set_argument("-a", "--answer", default=42, type=int)
        def run(origin, destination, speed=1, **kwargs):
            return {"task": "run", "origin": origin, "destination": destination, "speed": speed, "kwargs": kwargs}

        # noinspection PyUnusedLocal
        @self.task_manager
        def fly(origin, destination, *args):
            return {"task": "fly", "origin": origin, "destination": destination, "args": args}

        with six.assertRaisesRegex(self, ArgumentTypeError,
                                   r"^cannot find task to execute\. \(choose from 'run', 'fly'\)$" if six.PY3
                                   else r"^too few arguments$"):
            self.task_manager.dispatch(args=(), raise_exception=True)

        with six.assertRaisesRegex(self, ArgumentTypeError,
                                   r"^the following arguments are required: origin, destination$" if six.PY3
                                   else r"^too few arguments$"):
            self.task_manager.dispatch(args=("run",), raise_exception=True)

        with six.assertRaisesRegex(self, ArgumentTypeError,
                                   r"^the following arguments are required: destination$" if six.PY3
                                   else r"^too few arguments$"):
            self.task_manager.dispatch(args=("run", "tokyo",), raise_exception=True)

        self.assertEqual(
            {"task": "run", "origin": "tokyo", "destination": "osaka", "speed": 1, "kwargs": {"answer": 42}},
            self.task_manager.dispatch(args=("run", "tokyo", "osaka",))
        )
        self.assertEqual(
            {"task": "run", "origin": "tokyo", "destination": "osaka", "speed": 100, "kwargs": {"answer": 42}},
            self.task_manager.dispatch(args=("run", "tokyo", "osaka", "-s", "100"))
        )
        self.assertEqual(
            {"task": "run", "origin": "tokyo", "destination": "osaka", "speed": 10, "kwargs": {"answer": 4242}},
            self.task_manager.dispatch(args=("run", "tokyo", "osaka", "--speed", "10", "-a", "4242"))
        )

        with six.assertRaisesRegex(self, ArgumentTypeError, r"^unrecognized arguments: '5656'$"):
            self.task_manager.dispatch(args=("run", "tokyo", "osaka", "5656"), raise_exception=True)

        self.assertEqual({"task": "fly", "origin": "tokyo", "destination": "osaka", "args": ("55", "66")},
                         self.task_manager.dispatch(args=("fly", "tokyo", "osaka", "55", "66",)))
        self.assertEqual({"task": "fly", "origin": "tokyo", "destination": "osaka", "args": ()},
                         self.task_manager.dispatch(args=("fly", "tokyo", "osaka",)))

    def test_dispatch_with_sys(self):
        @self.task_manager
        @self.task_manager.set_argument("-a", "--answer", default=42, type=int)
        def run(origin, destination, speed=1, **kwargs):
            return {"task": "run", "origin": origin, "destination": destination, "speed": speed, "kwargs": kwargs}

        # noinspection PyUnusedLocal
        @self.task_manager
        def fly(origin, destination, *args):
            return {"task": "fly", "origin": origin, "destination": destination, "args": args}

        original_argv = sys.argv

        sys.argv = [original_argv[0]]
        with six.assertRaisesRegex(self, ArgumentTypeError,
                                   r"^cannot find task to execute\. \(choose from 'run', 'fly'\)$" if six.PY3
                                   else r"^too few arguments$"):
            self.task_manager.dispatch(raise_exception=True)

        sys.argv = [original_argv[0], "run"]
        with six.assertRaisesRegex(self, ArgumentTypeError,
                                   r"^the following arguments are required: origin, destination$" if six.PY3
                                   else r"^too few arguments$"):
            self.task_manager.dispatch(raise_exception=True)

        sys.argv = [original_argv[0], "run", "tokyo"]
        with six.assertRaisesRegex(self, ArgumentTypeError,
                                   r"^the following arguments are required: destination$" if six.PY3
                                   else r"^too few arguments$"):
            self.task_manager.dispatch(raise_exception=True)

        sys.argv = [original_argv[0], "run", "tokyo", "osaka"]
        self.assertEqual(
            {"task": "run", "origin": "tokyo", "destination": "osaka", "speed": 1, "kwargs": {"answer": 42}},
            self.task_manager.dispatch()
        )
        sys.argv = [original_argv[0], "run", "tokyo", "osaka", "-s", "100"]
        self.assertEqual(
            {"task": "run", "origin": "tokyo", "destination": "osaka", "speed": 100, "kwargs": {"answer": 42}},
            self.task_manager.dispatch()
        )
        sys.argv = [original_argv[0], "run", "tokyo", "osaka", "--speed", "10", "-a", "4242"]
        self.assertEqual(
            {"task": "run", "origin": "tokyo", "destination": "osaka", "speed": 10, "kwargs": {"answer": 4242}},
            self.task_manager.dispatch()
        )

        sys.argv = [original_argv[0], "run", "tokyo", "osaka", "5656"]
        with six.assertRaisesRegex(self, ArgumentTypeError, r"^unrecognized arguments: '5656'$"):
            self.task_manager.dispatch(raise_exception=True)

        sys.argv = [original_argv[0], "fly", "tokyo", "osaka", "55", "66"]
        self.assertEqual({"task": "fly", "origin": "tokyo", "destination": "osaka", "args": ("55", "66")},
                         self.task_manager.dispatch())

        sys.argv = [original_argv[0], "fly", "tokyo", "osaka"]
        self.assertEqual({"task": "fly", "origin": "tokyo", "destination": "osaka", "args": ()},
                         self.task_manager.dispatch())

        sys.argv = original_argv

    def test_dispatch_without_raise_expection(self):
        @self.task_manager
        @self.task_manager.set_argument("-a", "--answer", default=42, type=int)
        def run(origin, destination, speed=1, **kwargs):
            return {"task": "run", "origin": origin, "destination": destination, "speed": speed, "kwargs": kwargs}

        # noinspection PyUnusedLocal
        @self.task_manager
        def fly(origin, destination, *args):
            return {"task": "fly", "origin": origin, "destination": destination, "args": args}

        message_template = ("usage: {prog} [-h] {{{{run,fly}}}} ...\n" +
                            "{{prog}}: error: {{error}}\n").format(
            prog=self.task_manager.parser.prog,
        )

        with capture_stdio() as captured_result, self.assertRaises(SystemExit):
            self.task_manager.dispatch(args=())
        self.assertEqual("", captured_result.captured_stdout)
        self.assertEqual(message_template.format(error=("cannot find task to execute. (choose from 'run', 'fly')"
                                                        if six.PY3 else "too few arguments"),
                                                 prog=self.task_manager.parser.prog),
                         captured_result.captured_stderr)

        with capture_stdio() as captured_result, self.assertRaises(SystemExit):
            self.task_manager.dispatch(args=("run",))
        self.assertEqual("", captured_result.captured_stdout)
        self.assertEqual(message_template.format(error=("the following arguments are required: origin, destination"
                                                        if six.PY3 else "too few arguments"),
                                                 prog=run.parser.prog),
                         captured_result.captured_stderr)

        with capture_stdio() as captured_result, self.assertRaises(SystemExit):
            self.task_manager.dispatch(args=("run", "tokyo"))
        self.assertEqual("", captured_result.captured_stdout)
        self.assertEqual(message_template.format(error=("the following arguments are required: destination" if six.PY3
                                                        else "too few arguments"),
                                                 prog=run.parser.prog),
                         captured_result.captured_stderr)

        with capture_stdio() as captured_result, self.assertRaises(SystemExit):
            self.task_manager.dispatch(args=("run", "tokyo", "osaka", "5566"))
        self.assertEqual("", captured_result.captured_stdout)
        self.assertEqual(message_template.format(error="unrecognized arguments: '5566'",
                                                 prog=run.parser.prog),
                         captured_result.captured_stderr)


class TaskManagerDecoratorTests(TaskManagerTests):

    # Decorator helpers

    def test_decorator_task_manager_identity_check(self):
        task_manager_1 = TaskManager()

        with self.assertRaises(AssertionError):
            @self.task_manager.main
            @task_manager_1
            def fly(origin, destination):
                return "Fly from {} to {}".format(origin, destination)

    def test_task_decorator(self):
        class SubTaskManager(TaskManager):
            def __init__(self):
                super(SubTaskManager, self).__init__()
                self.captured_msg = None

            @task_manager_decorator
            def yo(self, task):
                return task

            @task_manager_decorator
            def msg(self, task, msg):
                self.captured_msg = msg
                return task

        task_manager = SubTaskManager()

        @task_manager.yo
        def run(origin, destination):
            """Run from origin to destination"""
            return "Run from {} to {}".format(origin, destination)

        @task_manager.msg("Hello")
        def fly(origin, destination):
            """Fly from origin to destination"""
            return "Fly from {} to {}".format(origin, destination)

        self.assertIsNotNone(run)
        self.assertIsInstance(run, Task)
        self.assertEqual("run", run.__name__)
        self.assertEqual("Run from origin to destination", run.__doc__)

        self.assertIsNotNone(fly)
        self.assertIsInstance(fly, Task)
        self.assertEqual("fly", fly.__name__)
        self.assertEqual("Fly from origin to destination", fly.__doc__)
        self.assertEqual("Hello", task_manager.captured_msg)

    # Defined decorators

    def test_call(self):
        @self.task_manager
        def run(origin, destination):
            return "Run from {} to {}".format(origin, destination)

        self.assertIsInstance(run, Task)
        self.assertEqual("run", run.name)
        self.assertEqual("Run from Tokyo to Osaka", run("Tokyo", "Osaka"))

    def test_main_task(self):
        @self.task_manager
        def run(origin, destination):
            return "Run from {} to {}".format(origin, destination)

        @self.task_manager.main
        def fly(origin, destination):
            return "Fly from {} to {}".format(origin, destination)

        self.assertEqual(fly, self.task_manager.main_task)

    def test_set_name(self):
        @self.task_manager.set_name("Run")
        def run(origin, destination):
            return "Run from {} to {}".format(origin, destination)

        self.assertEqual("Run", run.name)

    def test_set_argument(self):
        @self.task_manager.set_argument("origin", help="XD")
        def run(origin, destination):
            return "Run from {} to {}".format(origin, destination)

        self.assertDictEqual(OrderedDict((
            ("origin", ("*", ("origin",), {"help": "XD"})),
            ("destination", ("*", ("destination", ), {"type": six.text_type})),
        )), run.registered_arguments)

    def test_set_group_argument(self):
        @self.task_manager.set_group_argument("location", "origin", help="XD")
        def run(origin, destination):
            return "Run from {} to {}".format(origin, destination)

        self.assertEqual(OrderedDict((
            ("origin", ("location", ("origin",), {"help": "XD"})),
            ("destination", ("*", ("destination",), {"type": six.text_type})),
        )), run.registered_arguments)
