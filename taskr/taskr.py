#
# Copyright 2014 sodastsai
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

import argparse
import functools
import inspect
import weakref
from collections import OrderedDict


# Task Info
# ======================================================================================================================

class _TaskInfo(object):

    def __init__(self, func):
        self.weak_function = weakref.ref(func)
        self.name = func.__name__
        self.arguments = OrderedDict()
        self.pass_namespace = False


# Task
# ======================================================================================================================

class Task(object):

    parser = None
    subparsers = None

    # Setup
    # ------------------------------------------------------------------------------------------------------------------

    @classmethod
    def setup(cls, *args, **kwargs):
        # Argument parser
        cls.parser = argparse.ArgumentParser(*args, **kwargs)

    @classmethod
    def setup_action(cls, *args, **kwargs):
        # setup parser
        if not cls.parser:
            cls.setup()

        if 'title' not in kwargs:
            kwargs['title'] = 'Action'
        cls.subparsers = cls.parser.add_subparsers(*args, **kwargs)

    # Register and execution
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self, func, assigned=functools.WRAPPER_ASSIGNMENTS):
        # setup base
        if not self.parser:
            self.setup()
        if not self.subparsers:
            self.setup_action()

        self.function = func
        # Keep attributes (like functools.wraps
        for attr in assigned:
            setattr(self, attr, getattr(func, attr))

        task_info = self._get_task_info(self.function)

        # Register this task to argparse
        parser = self.subparsers.add_parser(task_info.name)
        parser.set_defaults(__instance__=self)

        # Register arguments
        manual_arguments = task_info.arguments
        if task_info.pass_namespace:
            # Register arguments by decorator declaration
            for _ in reversed(manual_arguments):
                arg_args, arg_kwargs = manual_arguments[_]
                parser.add_argument(*arg_args, **arg_kwargs)
        else:
            # Register arguments by function spec

            # Get argument spec of function
            try:
                arg_spec = inspect.getfullargspec(task_info.weak_function())
            except AttributeError:
                arg_spec = inspect.getargspec(task_info.weak_function())
            # Parse argument spec into args list and kwargs dict
            if arg_spec.defaults:
                args = arg_spec.args[:-len(arg_spec.defaults)]
                kwargs = dict(zip(arg_spec.args[-len(arg_spec.defaults):], arg_spec.defaults))
            else:
                args = arg_spec.args
                kwargs = {}

            # Register
            for arg_name in args:
                if arg_name in manual_arguments:
                    arg_args, arg_kwargs = manual_arguments[arg_name]
                    parser.add_argument(*arg_args, **arg_kwargs)
                else:
                    parser.add_argument(arg_name)
            for kwarg_name, default_value in kwargs.items():
                arg_name = '--' + kwarg_name.replace('_', '-')
                use_kwarg_name = kwarg_name in manual_arguments
                if use_kwarg_name or arg_name in manual_arguments:
                    arg_args, arg_kwargs = manual_arguments[(use_kwarg_name and kwarg_name or arg_name)]
                    if 'default' not in arg_kwargs:
                        arg_kwargs['default'] = default_value
                    parser.add_argument(*arg_args, **arg_kwargs)
                else:
                    parser.add_argument(arg_name, default=default_value)

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def __repr__(self):
        return repr(self.function)

    # Dispatch
    # ------------------------------------------------------------------------------------------------------------------

    @classmethod
    def dispatch(cls):
        args = cls.parser.parse_args()
        if hasattr(args, '__instance__'):
            task_object = args.__instance__
            if cls._get_task_info(task_object).pass_namespace:
                task_object(args)
            else:
                kwargs = dict(vars(args))
                del kwargs['__instance__']
                task_object(**kwargs)
        else:
            cls.parser.print_help()

    # Decorators
    # ------------------------------------------------------------------------------------------------------------------

    @classmethod
    def set_name(cls, name):
        def decorator(func):
            cls._get_task_info(func).name = name

            @functools.wraps(func)
            def wrapper(*func_args, **func_kwargs):
                return func(*func_args, **func_kwargs)
            return wrapper
        return decorator

    @classmethod
    def set_argument(cls, *args, **kwargs):
        def decorator(func):

            task_info = cls._get_task_info(func)
            if 'dest' in kwargs:
                task_info.arguments[kwargs['dest']] = (args, kwargs)
            else:
                # Register each argparse argument name for mapping function argument
                for arg in args:
                    task_info.arguments[arg] = (args, kwargs)

            @functools.wraps(func)
            def wrapper(*func_args, **func_kwargs):
                return func(*func_args, **func_kwargs)

            return wrapper

        return decorator

    @classmethod
    def pass_argparse_namespace(cls, func):

        cls._get_task_info(func).pass_namespace = True

        @functools.wraps(func)
        def wrapper(*func_args, **func_kwargs):
            return func(*func_args, **func_kwargs)
        return wrapper

    # Utils
    # ------------------------------------------------------------------------------------------------------------------

    # noinspection PyProtectedMember
    @classmethod
    def _get_task_info(cls, func_or_task):
        if isinstance(func_or_task, Task):
            return cls._get_task_info(func_or_task.function)

        if callable(func_or_task):
            if not hasattr(func_or_task, '_taskr_info'):
                func_or_task._taskr_info = _TaskInfo(func_or_task)
            return func_or_task._taskr_info
        return None
