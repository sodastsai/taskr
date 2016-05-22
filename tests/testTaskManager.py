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

import six

from taskr.taskr import Task, TaskManager, task_manager_decorator


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
