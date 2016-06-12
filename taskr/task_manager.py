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

import six

from .argparse import ArgumentParser, ArgumentTypeError
from .parameters import parameters_of_function
from .task import Task


def task_manager_decorator(tm_method):
    """
    :type tm_method: function
    :rtype: function
    """
    args_count = len(parameters_of_function(tm_method))
    assert args_count >= 2, "Unsupported method signature of TaskManager"

    if args_count > 2:
        @six.wraps(tm_method)
        def wrapper(tm, *tmm_args, **tmm_kwargs):
            """
            :type tm: TaskManager
            :type tmm_args: tuple
            :type tmm_kwargs: dict
            :rtype: function
            """
            def wrapped(task):
                return tm_method(tm, tm.get_or_create_task_object(task), *tmm_args, **tmm_kwargs)
            return wrapped
    else:
        @six.wraps(tm_method)
        def wrapper(tm, task, *tmm_args, **tmm_kwargs):
            """
            :type tm: TaskManager
            :type task: Task
            :type tmm_args: tuple
            :type tmm_kwargs: dict
            :rtype: Task
            """
            return tm_method(tm, tm.get_or_create_task_object(task), *tmm_args, **tmm_kwargs)

    return wrapper


@six.python_2_unicode_compatible
class TaskManager(object):

    def __init__(self):
        super(TaskManager, self).__init__()

        self.tasks = []
        """:type: list[Task]"""
        self.main_task = None  # type: Task

        # Argument parsers
        self.parser = ArgumentParser()
        self.task_subparser = self.parser.add_subparsers(title='Task')
        self._tasks_finalized = False

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self)

    def __str__(self):
        string = "tasks=[{}]".format(",".join((task.name for task in self.tasks)))
        if self.main_task:
            string += ", main={}".format(self.main_task.name)
        return string

    def __contains__(self, task):
        if not isinstance(task, Task):
            return False
        return task in self.tasks

    def get_or_create_task_object(self, task_or_callable):
        """
        :type task_or_callable: function|Task
        :rtype: Task
        """
        if isinstance(task_or_callable, Task):
            assert task_or_callable.task_manager == self, "Missmatched task and task manager."
            return task_or_callable
        elif callable(task_or_callable):
            task_obj = Task(task_or_callable, self)
            self.tasks.append(task_obj)
            return task_obj
        else:
            raise ValueError("{} object is not a callable".format(task_or_callable))

    def finalize(self):
        if not self._tasks_finalized:
            for task in self.tasks:
                task.finalize_argparser()
            self._tasks_finalized = True

    def parse(self, args):
        """
        :type args: tuple[str]
        :rtype: (Task, tuple, dict)
        """
        assert self._tasks_finalized, "Tasks should be finalized before parsing arguments."

        task_kwargs, task_args = self.parser.parse_args(args=args)

        task = task_kwargs.pop("__task__", None)  # type: Task
        if task is None:
            raise ArgumentTypeError("cannot find task to execute. (choose from {})".format(
                ", ".join(("'{}'".format(task.name) for task in self.tasks))
            ), self.parser)

        if task_args and not task.has_var_positional:
            raise ArgumentTypeError("unrecognized arguments: {}".format(
                ", ".join(("'{}'".format(task_arg) for task_arg in task_args))
            ), task.parser)
        else:
            task_args = tuple((task_kwargs.pop(param.name) for param in task.positional_parameters)) + task_args

        return task, task_args, task_kwargs

    def dispatch(self, args=None, raise_exception=False):
        self.finalize()
        args = args if args is not None else sys.argv[1:]
        try:
            task, task_args, task_kwargs = self.parse(args=args)
        except ArgumentTypeError as e:
            if raise_exception:
                raise
            else:
                self.parser.print_usage(sys.stderr)
                sys.stderr.write("{!r}\n".format(e))
                sys.exit(1)

        return task(*task_args, **task_kwargs)

    # Decorator

    @task_manager_decorator
    def __call__(self, task):
        """
        :type task: Task
        :rtype: Task
        """
        return task

    @task_manager_decorator
    def main(self, task):
        """
        :type task: Task
        :rtype: Task
        """
        self.main_task = task
        return task

    @task_manager_decorator
    def set_name(self, task, name):
        """
        :type task: Task
        :type name: str|unicode
        :rtype: Task
        """
        task.name = name
        return task

    @task_manager_decorator
    def set_argument(self, task, *args, **kwargs):
        """
        :type task: Task
        :type args: tuple
        :type kwargs: dict
        :rtype: Task
        """
        task.set_argument(*args, **kwargs)
        return task

    @task_manager_decorator
    def set_group_argument(self, task, *args, **kwargs):
        """
        :type task: Task
        :type args: tuple
        :type kwargs: dict
        :rtype: Task
        """
        task.set_group_argument(*args, **kwargs)
        return task
