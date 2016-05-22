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

from taskr.taskr import Task, TaskManager


def run(origin, destination):
    return "Run from {} to {}".format(origin, destination)


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
