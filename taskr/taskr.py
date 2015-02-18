#
# Copyright 2014-2015 sodastsai
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
from collections import OrderedDict
import inspect
import functools
import six
import sys
import types
import weakref


class TaskManager(object):

    def __init__(self):
        # Argument parsers
        self.parser = argparse.ArgumentParser()
        self.action_subparser = self.parser.add_subparsers(title='Action')

        # Exception handling
        self.should_raise_exceptions = False

        # Executing info
        self.executing_task_object = None
        """:type: Task"""
        self._main_task = None

        self.pool = {}

    @property
    def help_text(self):
        return self.parser.epilog

    @help_text.setter
    def help_text(self, help_text):
        self.parser.epilog = help_text

    @property
    def main_task(self):
        """
        :rtype: Task
        """
        # noinspection PyCallingNonCallable
        return self._main_task() if self._main_task else None

    @main_task.setter
    def main_task(self, obj):
        """
        :type obj: Task
        """
        self._main_task = weakref.ref(obj) if obj else None

    def _task_object(self, callable_obj):
        """
        :rtype: Task
        """
        if isinstance(callable_obj, Task):
            return callable_obj
        elif callable(callable_obj):
            return Task(callable_obj, self)
        else:
            raise ValueError('{} object is not callable'.format(callable_obj))

    def _call_cleanup_func(self):
        if self.executing_task_object:
            self.executing_task_object.cleanup_function(self.executing_task_object)

    # Decorators -------------------------------------------------------------------------------------------------------

    def __call__(self, callable_obj):
        """
        :rtype: Task
        """
        task_object = self._task_object(callable_obj)
        task_object.setup_argparser()
        return task_object

    def pass_argparse_namespace(self, callable_obj):
        task_object = self._task_object(callable_obj)
        task_object.pass_argparse_namespace = True
        return task_object

    def main(self, callable_obj):
        task_object = self._task_object(callable_obj)
        task_object.manager.main_task = task_object
        return task_object

    def set_name(self, task_name):
        def wrapper(callable_obj):
            task_object = self._task_object(callable_obj)
            task_object.name = task_name
            return task_object
        return wrapper

    def set_exit_cleanup(self, cleanup_func):
        def wrapper(callable_obj):
            task_object = self._task_object(callable_obj)
            task_object.cleanup_function = cleanup_func
            return task_object
        return wrapper

    def set_group_argument(self, group, *args, **kwargs):
        def wrapper(callable_obj):
            task_object = self._task_object(callable_obj)

            if args[0].startswith('-'):
                # Optional
                dest = kwargs.get('dest', None)
                if not dest:
                    dest = args[0]
                    """:type: str"""
                    while dest.startswith('-'):
                        dest = dest[1:]
                    dest = dest.replace('-', '_')
                task_object.manual_arguments[dest] = (group, args, kwargs)
            else:
                # Positional
                task_object.manual_arguments[kwargs.get('dest', args[0])] = (group, args, kwargs)

            return task_object
        return wrapper

    def set_argument(self, *args, **kwargs):
        return self.set_group_argument('*', *args, **kwargs)

    def alias(self, name):
        def wrapper(callable_obj):
            task_object = self._task_object(callable_obj)
            task_object.aliases.append(name)
            return task_object
        return wrapper

    def help(self, help_text):
        def wrapper(callable_obj):
            task_object = self._task_object(callable_obj)
            task_object.help_text = help_text
            return task_object
        return wrapper

    # Dispatch ---------------------------------------------------------------------------------------------------------

    def dispatch(self):
        # Setup action name if manager has main task
        in_args = sys.argv[1:]
        if self.main_task:  # main_task is a weak reference to task
            in_args = [self.main_task.name] + in_args

        # Parse argument
        args = self.parser.parse_args(in_args)
        if hasattr(args, '__instance__'):
            task_object = args.__instance__
            """:type: Task"""
            self.executing_task_object = task_object

            if task_object.pass_argparse_namespace:
                task_object.arguments = args
                call_args = (args,)
                call_kwargs = {}
            else:
                kwargs = dict(vars(args))
                kwargs.pop('__instance__')
                task_object.arguments = kwargs
                call_args = ()
                call_kwargs = kwargs

            try:
                task_object(*call_args, **call_kwargs)
            except (Exception, KeyboardInterrupt) as e:
                if self.should_raise_exceptions:
                    self._call_cleanup_func()
                    raise
                else:
                    self.exit(status=1, message='Error: {}\n'.format(e))
        else:
            self.parser.print_help()

    # Error ------------------------------------------------------------------------------------------------------------

    def exit(self, status=0, message=None):
        self._call_cleanup_func()
        if message and not message.endswith('\n'):
            message += '\n'
        self.parser.exit(status, message)

    def error(self, message):
        self._call_cleanup_func()
        if not message.endswith('\n'):
            message += '\n'
        self.parser.error(message)


class Task(object):

    def __init__(self, callable_obj, manager):
        """
        :type callable_obj: callable
        :type manager: TaskManager
        """
        self.callable = callable_obj
        functools.update_wrapper(self, self.callable)
        self.callable_is_object = not isinstance(self.callable, types.FunctionType)
        self.name = self.callable.__name__.replace('_', '-').lower()
        self.arguments = {}

        self.manual_arguments = OrderedDict()
        self.pass_argparse_namespace = False
        self.cleanup_function = lambda x: None

        self.manager = manager
        self.parser = None
        """:type: argparse.ArgumentParser"""
        self.argument_groups = None
        self.aliases = []
        self.help_text = None

    def __call__(self, *args, **kwargs):
        self.callable(*args, **kwargs)

    def setup_argparser(self):
        add_parser_kwargs = {}
        if six.PY3:
            add_parser_kwargs['aliases'] = self.aliases
        if self.help_text:
            add_parser_kwargs['help'] = self.help_text
        self.parser = self.manager.action_subparser.add_parser(self.name, **add_parser_kwargs)
        self.parser.set_defaults(__instance__=self)
        self.argument_groups = {'*': self.parser}

        if self.pass_argparse_namespace:
            # Register arguments by decorator declaration
            for _ in reversed(self.manual_arguments):
                group, arg_args, arg_kwargs = self.manual_arguments[_]
                self._get_argument_group(group).add_argument(*arg_args, **arg_kwargs)
        else:
            # Register arguments by function spec
            # Get argument spec of function
            func_to_inspect = self.callable.__call__ if self.callable_is_object else self.callable
            arg_spec = (inspect.getfullargspec if six.PY3 else inspect.getargspec)(func_to_inspect)
            # Parse argument spec into args list and kwargs dict
            if arg_spec.defaults:
                args = arg_spec.args[:-len(arg_spec.defaults)]
                kwargs = dict(zip(arg_spec.args[-len(arg_spec.defaults):], arg_spec.defaults))
            else:
                args = arg_spec.args
                kwargs = {}
            # Remove 'self' of object method args
            if self.callable_is_object:
                args = args[1:]

            # Register
            for arg_name in args:
                group, arg_args, arg_kwargs = self.manual_arguments.get(arg_name, ('*', (arg_name,), {}))
                self._get_argument_group(group).add_argument(*arg_args, **arg_kwargs)
            for kwarg_name, default_value in kwargs.items():
                group, arg_args, arg_kwargs = self.manual_arguments.get(kwarg_name,
                                                                        ('*',
                                                                         ('--' + kwarg_name.replace('_', '-'),),
                                                                         {}))

                if 'default' not in arg_kwargs:
                    arg_kwargs['default'] = default_value

                self._get_argument_group(group).add_argument(*arg_args, **arg_kwargs)

    def _get_argument_group(self, group):
        """
        :type group: str
        :rtype: argparse.ArgumentParser
        """
        if isinstance(group, tuple):
            group_title, group_description = group
        else:
            group_title = group
            group_description = None

        if group_title not in self.argument_groups:
            self.argument_groups[group_title] = self.parser.add_argument_group(title=group_title,
                                                                               description=group_description)
        return self.argument_groups[group_title]
