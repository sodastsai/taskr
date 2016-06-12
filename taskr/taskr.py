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
import functools
from collections import OrderedDict

import six

from .argparse import ArgumentParser
from .decorators.once import oncemethod
from .parameters import parameters_of_function, ParameterClass


# ----------------------------------------------------------------------------------------------------------------------

def task_manager_decorator(tm_method):
    """
    :type tm_method: function
    :rtype: function
    """
    args_count = len(parameters_of_function(tm_method))
    assert args_count >= 2, "Unsupported method signature of TaskManager"

    if args_count > 2:
        @functools.wraps(tm_method)
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
        @functools.wraps(tm_method)
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
        self.action_subparser = self.parser.add_subparsers(title='Action')
        self._tasks_finalized = False

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self)

    def __str__(self):
        string = "tasks=[{}]".format(",".join((task.name for task in self.tasks)))
        if self.main_task:
            string += ", main={}".format(self.main_task.name)
        return string

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


# ----------------------------------------------------------------------------------------------------------------------

@six.python_2_unicode_compatible
class Task(object):

    def __init__(self, callable_obj, task_manager):
        """
        :type callable_obj: callable
        :type task_manager: TaskManager
        """
        self.callable = callable_obj
        functools.update_wrapper(self, self.callable)
        self.name = self.callable.__name__.replace("_", "-").lower()

        self.task_manager = task_manager

        # Parse default registered arguments from the callable object
        self.has_var_keyword = False
        self.has_var_positional = False
        self._argparser_finalized = False
        self.positional_arguments = None
        """:type: tuple[str]"""
        self.registered_arguments = OrderedDict()
        """:type : dict[str, tuple]"""
        for arg_name, parameter in self.raw_parameters.items():
            parameter_args = (arg_name,)
            parameter_kwargs = {}
            # default value and optional
            if parameter.default != ParameterClass.empty:
                parameter_kwargs["default"] = parameter.default
                parameter_kwargs["required"] = False
                parameter_args = ("-{}".format(arg_name[0]), "--{}".format(arg_name.replace("_", "-")))
            # action of this parameter
            if isinstance(parameter.default, bool):
                parameter_kwargs["action"] = "store_false" if parameter.default else "store_true"
            if "action" not in parameter_kwargs or parameter_kwargs["action"] in ("store", "append"):
                if parameter.default != ParameterClass.empty and parameter.default is not None:
                    parameter_kwargs["type"] = parameter.default.__class__
                else:
                    parameter_kwargs["type"] = six.text_type
            # kind of this parameter
            if parameter.kind == ParameterClass.VAR_POSITIONAL:
                self.has_var_positional = True
                continue
            elif parameter.kind == ParameterClass.VAR_KEYWORD:
                self.has_var_keyword = True
                continue

            self.registered_arguments[arg_name] = ("*", parameter_args, parameter_kwargs)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self)

    def __str__(self):
        return self.name

    def __call__(self, *args, **kwargs):
        return self.callable(*args, **kwargs)

    @property
    @oncemethod("_parser")
    def parser(self):
        parser = self.task_manager.action_subparser.add_parser(self.name)
        """:type: argparse.ArgumentParser"""
        parser.set_defaults(__task__=self)
        return parser

    def finalize_argparser(self):
        assert not self._argparser_finalized,\
            "The argument parser of {} has been finalized. Cannot finalize again.".format(self)
        self._argparser_finalized = True

        parsers_groups = {"*": self.parser}
        """:type : dict[str, argparse.ArgumentParser]"""

        def create_argument_group(argument_group):
            return self.parser.add_argument_group(title=argument_group)

        positional_arguments = []
        for group, add_args, add_kwargs in self.registered_arguments.values():
            if len(add_args) == 1 and not add_args[0].startswith("-"):
                positional_arguments.append(add_args[0])
            parser = parsers_groups.setdefault(group, create_argument_group(group))  # type: argparse.ArgumentParser
            parser.add_argument(*add_args, **add_kwargs)

        self.positional_arguments = tuple(positional_arguments)

    # Parameters

    @property
    @oncemethod("_raw_parameters")
    def raw_parameters(self):
        return parameters_of_function(self.callable)

    def set_group_argument(self, group, *args, **kwargs):
        assert not self._argparser_finalized, \
            "The argument parser of {} has been finalized. Cannot add new arguments.".format(self)

        # Check argument Type
        args_count = len(args)
        assert args_count >= 1, "Expect at least one name or flag when calling `set_group_argument`."
        positional_argument = all((not arg.startswith("-") for arg in args))

        # Find destination of this argument
        if positional_argument:
            dest = kwargs.get("dest", args[0])
        else:  # Optional
            dest = kwargs.get('dest', None)
            if not dest:
                # Find from args .... use the name of first "--" arguments
                for arg in args:
                    if not arg.startswith('--'):
                        continue
                    dest = arg.lstrip('-').replace('-', '_')
                    break
            if not dest:
                # Raise exception
                raise ValueError("Cannot find destination of the flags '{}' for {}".format(', '.join(args), self))

        # Register
        if not self.has_var_keyword and dest not in self.raw_parameters:
            raise ValueError("\"{}\" is not allowed to be added as an argument of {}."
                             " {} doesn't accept extra keyword args.".format(dest, self.name, self.name))
        self.registered_arguments[dest] = (group, args, kwargs)

    def set_argument(self, *args, **kwargs):
        self.set_group_argument('*', *args, **kwargs)
