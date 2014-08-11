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
import types
import sys
import weakref
from collections import OrderedDict


# Task Info
# ======================================================================================================================

class _TaskInfo(object):

    def __init__(self, func):
        if inspect.isclass(func):
            if hasattr(func, 'taskr_instance'):
                func = func.taskr_instance
            else:
                func_class = func
                func = func_class()
                functools.update_wrapper(func, func_class)
                func_class.taskr_instance = func

        self.weak_function = weakref.ref(func)
        self.name = func.__name__.replace('_', '-').lower()
        self.arguments = OrderedDict()
        self.pass_namespace = False
        self.has_main_func = False

    @property
    def function(self):
        return self.weak_function()

    def add_argument(self, group, *args, **kwargs):
        if args[0].startswith('-'):
            # Optional
            if 'dest' in kwargs:
                self.arguments[kwargs['dest']] = (group, args, kwargs)
            else:
                raise AttributeError('Optional argument must provide "dest"')
        else:
            # Positional
            self.arguments[kwargs.get('dest', args[0])] = (group, args, kwargs)


# Task
# ======================================================================================================================

class Task(object):

    # Setup
    # ------------------------------------------------------------------------------------------------------------------

    _parser = None
    main_func_name = None

    @classmethod
    def parser(cls):
        if not cls._parser:
            cls.setup()
        return cls._parser

    @classmethod
    def setup(cls, *args, **kwargs):
        # Argument parser
        cls._parser = argparse.ArgumentParser(*args, **kwargs)

    _subparsers = None

    @classmethod
    def subparsers(cls):
        if not cls._subparsers:
            cls.setup_action()
        return cls._subparsers

    @classmethod
    def setup_action(cls, *args, **kwargs):
        if 'title' not in kwargs:
            kwargs['title'] = 'Action'
        cls._subparsers = cls.parser().add_subparsers(*args, **kwargs)

    # Register and execution
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self, func):
        self.function = func
        functools.update_wrapper(self, func)

        task_info = self._get_task_info(self.function)

        # Register this task to argparse
        self.local_parser = self.subparsers().add_parser(task_info.name)
        self.local_parser.set_defaults(__instance__=self)
        self.has_main_func = task_info.has_main_func

        # Register arguments
        manual_arguments = task_info.arguments
        self.argument_groups = {'*': self.local_parser}
        # Go
        if task_info.pass_namespace:
            # Register arguments by decorator declaration
            for _ in reversed(manual_arguments):
                group, arg_args, arg_kwargs = manual_arguments[_]
                self._get_argument_group(group).add_argument(*arg_args, **arg_kwargs)
        else:
            # Register arguments by function spec
            # Get argument spec of function
            self.function_is_object = not isinstance(task_info.function, types.FunctionType)
            func_to_inspect = task_info.function.__call__ if self.function_is_object else task_info.function
            try:
                arg_spec = inspect.getfullargspec(func_to_inspect)
            except AttributeError:
                arg_spec = inspect.getargspec(func_to_inspect)
            # Parse argument spec into args list and kwargs dict
            if arg_spec.defaults:
                args = arg_spec.args[:-len(arg_spec.defaults)]
                kwargs = dict(zip(arg_spec.args[-len(arg_spec.defaults):], arg_spec.defaults))
            else:
                args = arg_spec.args
                kwargs = {}
            # Remove 'self' of object method args
            if self.function_is_object:
                args = args[1:]

            # Register
            for arg_name in args:
                group, arg_args, arg_kwargs = manual_arguments.get(arg_name, ('*', (arg_name,), {}))
                self._get_argument_group(group).add_argument(*arg_args, **arg_kwargs)
            for kwarg_name, default_value in kwargs.items():
                group, arg_args, arg_kwargs = manual_arguments.get(kwarg_name,
                                                                   ('*', ('--' + kwarg_name.replace('_', '-'),), {}))

                if 'default' not in arg_kwargs:
                    arg_kwargs['default'] = default_value

                self._get_argument_group(group).add_argument(*arg_args, **arg_kwargs)

    def __call__(self, *args, **kwargs):
        return self._get_task_info(self.function).function(*args, **kwargs)

    def __repr__(self):
        return repr(self.function)

    # Dispatch
    # ------------------------------------------------------------------------------------------------------------------

    @classmethod
    def dispatch(cls):
        in_args = sys.argv[1:]
        if cls.main_func_name is not None:
            in_args = [cls.main_func_name] + in_args

        args = cls.parser().parse_args(in_args)
        if hasattr(args, '__instance__'):
            task_object = args.__instance__
            if cls._get_task_info(task_object).pass_namespace:
                task_object(args)
            else:
                kwargs = dict(vars(args))
                del kwargs['__instance__']
                task_object(**kwargs)
        else:
            cls.parser().print_help()

    # Decorators
    # ------------------------------------------------------------------------------------------------------------------

    @classmethod
    def main(cls, func):
        cls._get_task_info(func).has_main_func = True
        cls.main_func_name = func.__name__

        @functools.wraps(func)
        def wrapper(*func_args, **func_kwargs):
            return func(*func_args, **func_kwargs)
        return wrapper

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
    def set_group_argument(cls, group, *args, **kwargs):
        def decorator(func):
            cls._get_task_info(func).add_argument(group, *args, **kwargs)

            @functools.wraps(func)
            def wrapper(*func_args, **func_kwargs):
                return func(*func_args, **func_kwargs)
            return wrapper
        return decorator

    @classmethod
    def set_argument(cls, *args, **kwargs):
        return cls.set_group_argument('*', *args, **kwargs)

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
    def _get_task_info(cls, func):
        if not hasattr(func, '_taskr_info'):
            func._taskr_info = _TaskInfo(func)
        return func._taskr_info

    @property
    def task_info(self):
        return self._get_task_info(self.function)

    def _get_argument_group(self, group):
        if isinstance(group, tuple):
            group_title, group_description = group
        else:
            group_title = group
            group_description = None

        if group_title not in self.argument_groups:
            self.argument_groups[group_title] = self.local_parser.add_argument_group(title=group_title,
                                                                                     description=group_description)
        return self.argument_groups[group_title]

    @classmethod
    def exit(cls, status=0, message=None):
        if message and not message.endswith('\n'):
            message += '\n'
        cls.parser().exit(status, message)

    @classmethod
    def error(cls, message):
        if not message.endswith('\n'):
            message += '\n'
        cls.parser().error(message)
