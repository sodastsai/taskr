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
import functools
import inspect
import os
import re
import sys
import types
import weakref
from collections import OrderedDict
from copy import deepcopy

import six

from .argparser import ArgumentParser, ArgumentParserError
from .terminal import Color, Console

whitespace_pattern = re.compile(r'\s+')
prefix_whitespace_pattern = re.compile(r'^\s+')


# noinspection PyPep8Naming
class _task_manager_method_decorator(object):

    def __init__(self, with_arguments):
        self.with_arguments = with_arguments

    def __call__(self, task_manager_method):
        if self.with_arguments:
            def task_manager_method_wrapper(task_instance, *task_manager_method_args, **task_manager_method_kwargs):
                """
                :type task_instance: TaskManager
                :type task_manager_method_args: tuple
                :type task_manager_method_kwargs: dict
                """
                def callable_wrapper(callable_obj):
                    # noinspection PyProtectedMember
                    task_object = task_instance._get_or_create_task_object(callable_obj)
                    task_manager_method(task_instance, task_object,
                                        *task_manager_method_args, **task_manager_method_kwargs)
                    return task_object
                return callable_wrapper
        else:
            def task_manager_method_wrapper(task_instance, callable_obj):
                """
                :type task_instance: TaskManager
                :type callable_obj: function
                """
                # noinspection PyProtectedMember
                task_object = task_instance._get_or_create_task_object(callable_obj)
                task_manager_method(task_instance, task_object)
                return task_object

        return task_manager_method_wrapper


class TaskrHelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


class TaskManager(object):

    def __init__(self):
        self._tasks = set()
        """:type: set[Task]"""

        # Argument parsers
        self.parser = ArgumentParser(formatter_class=TaskrHelpFormatter)
        self.action_subparser = self.parser.add_subparsers(title='Action')

        # Exception handling
        self.should_raise_exceptions = int(os.environ.get('TASKR_RAISE_EXCEPTION', '0')) != 0
        self.exit_code = 0

        # Executing info
        self._executing_task = None
        """:type: Task"""
        self._main_task = None

        self.pool = {}

    @property
    def tasks(self):
        """
        :rtype: set[Task]
        """
        return self._tasks

    @property
    def executing_task(self):
        return self._executing_task

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

    def _get_or_create_task_object(self, callable_obj):
        """
        :rtype: Task
        """
        if isinstance(callable_obj, Task):
            return callable_obj
        elif callable(callable_obj):
            task_obj = Task(callable_obj, self)
            self._tasks.add(task_obj)
            return task_obj
        else:
            raise ValueError('{} object is not callable'.format(callable_obj))

    def _call_cleanup_func(self):
        if self._executing_task:
            self._executing_task.cleanup_function(self._executing_task)

    # Decorators -------------------------------------------------------------------------------------------------------

    @_task_manager_method_decorator(with_arguments=False)
    def __call__(self, task_object):
        pass  # Keep for generating task object (by the decorator)

    @_task_manager_method_decorator(with_arguments=False)
    def pass_argparse_namespace(self, task_object):
        task_object.pass_argparse_namespace = True

    @_task_manager_method_decorator(with_arguments=False)
    def main(self, task_object):
        task_object.manager.main_task = task_object

    @_task_manager_method_decorator(with_arguments=True)
    def set_name(self, task_object, name):
        task_object.name = name

    @_task_manager_method_decorator(with_arguments=True)
    def set_exit_cleanup(self, task_object, cleanup_func):
        task_object.cleanup_function = cleanup_func

    @_task_manager_method_decorator(with_arguments=True)
    def set_group_argument(self, task_object, *args, **kwargs):
        task_object.set_group_argument(*args, **kwargs)

    @_task_manager_method_decorator(with_arguments=True)
    def set_argument(self, task_object, *args, **kwargs):
        task_object.set_argument(*args, **kwargs)

    @_task_manager_method_decorator(with_arguments=True)
    def alias(self, task_object, name):
        task_object.aliases.append(name)

    @_task_manager_method_decorator(with_arguments=True)
    def auto_create_short_arguments(self, task_object, auto_create_short_arguments):
        task_object.auto_create_short_arguments = auto_create_short_arguments

    @_task_manager_method_decorator(with_arguments=True)
    def help(self, task_object, help_text):
        task_object.help_text = help_text

    # Dispatch ---------------------------------------------------------------------------------------------------------

    def dispatch(self, args=None, keep_running_after_finished=False):
        # Setup arg-parser
        task_dict = {task.name: task for task in self.tasks}
        for task in self.tasks:
            task.setup_argparser()

        # Setup action name if manager has main task
        args = args or sys.argv[1:]
        if len(args) == 0 and self.main_task:
            args = [self.main_task.name]
        # Parse argument
        error_msg = None
        try:
            args = self.parser.parse_args(args)
            final_parser = self.parser
        except ArgumentParserError as e:
            error_msg = str(e)
            if len(args) > 0 and args[0] in task_dict:
                final_parser = task_dict[args[0]].parser
                args = argparse.Namespace()
            elif self.main_task:
                # Append main task if necessary
                if len(args) == 0 or args[0] != self.main_task.name:
                    args = [self.main_task.name] + args
                # Check for main task
                try:
                    args = self.parser.parse_args(args)
                except ArgumentParserError as e:
                    error_msg = str(e)
                    args = argparse.Namespace()
                finally:
                    final_parser = self.main_task.parser
            else:
                final_parser = self.parser
                args = argparse.Namespace()
        # dispatch or print help
        if hasattr(args, '__instance__'):
            # Call task object
            task_object = args.__instance__
            """:type: Task"""
            self._executing_task = task_object

            if task_object.pass_argparse_namespace:
                task_object.arguments = args
                call_args = (args,)
                call_kwargs = {}
            else:
                # noinspection PyTypeChecker
                kwargs = dict(vars(args))
                kwargs.pop('__instance__')
                task_object.arguments = deepcopy(kwargs)  # copy it
                if task_object.varargs in kwargs:
                    _varargs = kwargs.pop(task_object.varargs)
                    if not isinstance(_varargs, (list, tuple)):
                        _varargs = [_varargs]
                    call_args = _varargs
                else:
                    call_args = ()
                call_kwargs = kwargs

            try:
                task_object(*call_args, **call_kwargs)
            except BaseException as e:
                self._call_cleanup_func()
                if self.should_raise_exceptions:
                    raise
                elif not isinstance(e, SystemExit):
                    self.exit(status=1, message='Error: {}\n'.format(str(e) or e.__class__.__name__))
                else:
                    exit(getattr(e, 'code', -1))
            else:
                if not keep_running_after_finished:
                    self._call_cleanup_func()
                    sys.exit(self.exit_code)
        else:
            # Leave
            if error_msg:
                print('{}: error: {}\n'.format(final_parser.prog, error_msg))
            final_parser.print_help()
            self.exit(status=1)

    # Error ------------------------------------------------------------------------------------------------------------

    def exit(self, status=0, message=None, no_color=False):
        self._call_cleanup_func()
        if message and not message.endswith('\n'):
            message += '\n'
        if message and not no_color:
            message = Color.str(message, foreground=Console.error_color[0], light=Console.error_color[1])
        self.parser.exit(status, message)

    def error(self, message, no_color=False):
        self._call_cleanup_func()
        if not message.endswith('\n'):
            message += '\n'
        if message and not no_color:
            message = Color.str(message, foreground=Console.error_color[0], light=Console.error_color[1])
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
        self.auto_create_short_arguments = True
        self.pass_argparse_namespace = False
        self.cleanup_function = lambda x: None

        self.manager = manager
        self.parser = None
        """:type: argparse.ArgumentParser"""
        self.argument_groups = None
        self.aliases = []
        self.help_text = None
        self.strip_arguments_in_docstring = True

        self.args = ()
        self.kwargs = {}
        self.varargs = None
        """:type: str"""

    def __repr__(self):
        return '<Task: {}>'.format(self.name)

    def __str__(self):
        return repr(self)

    def __call__(self, *args, **kwargs):
        self.callable(*args, **kwargs)

    def parse_doc_str(self):
        if self.callable.__doc__ is None:
            return '', {}

        arguments = {}
        final_docs = []
        doc_lines = self.callable.__doc__.splitlines()
        doc_lines_global_indentation = None
        """:type: list[str]"""
        for line in doc_lines:
            if doc_lines_global_indentation is None:
                prefix_whitespace_match = prefix_whitespace_pattern.match(line)
                if prefix_whitespace_match:
                    doc_lines_global_indentation = prefix_whitespace_match.span()[1]

            line = line[(doc_lines_global_indentation or 0):]
            stripped_line = line.strip()
            if stripped_line.startswith(':param'):
                _, name, description = map(str.strip, stripped_line.split(':'))
                name = name.split(' ')[-1]
                if description:
                    arguments[name] = description
            else:
                final_docs.append(line)

        final_docs = '\n'.join(final_docs).strip()
        return final_docs, arguments

    def setup_argparser(self):
        task_description, task_args_description = self.parse_doc_str()

        add_parser_kwargs = {}
        if six.PY3:
            add_parser_kwargs['aliases'] = self.aliases
        if self.help_text:
            add_parser_kwargs['help'] = self.help_text
        add_parser_kwargs['formatter_class'] = TaskrHelpFormatter
        add_parser_kwargs['description'] = task_description
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
            if hasattr(arg_spec, 'kwonlydefaults') and arg_spec.kwonlydefaults:
                kwargs.update(arg_spec.kwonlydefaults)
            varargs = arg_spec.varargs
            # Remove 'self' of object method args
            if self.callable_is_object:
                args = args[1:]

            # Register
            for arg_name in args:
                group, arg_args, arg_kwargs = self.manual_arguments.get(arg_name, ('*', (arg_name,), {}))
                if 'help' not in arg_kwargs and arg_name in task_args_description:
                    arg_kwargs['help'] = task_args_description[arg_name]
                self._get_argument_group(group).add_argument(*arg_args, **arg_kwargs)

            for kwarg_name, default_value in kwargs.items():
                group, arg_args, arg_kwargs = self.manual_arguments.get(
                    kwarg_name,
                    (
                        # group
                        '*',
                        # arg_args
                        (('-' + kwarg_name[0],) if self.auto_create_short_arguments else ()) +
                        ('--' + kwarg_name.replace('_', '-'),),
                        # arg_kwargs
                        {},
                    )
                )

                if 'help' not in arg_kwargs and kwarg_name in task_args_description:
                    arg_kwargs['help'] = task_args_description[kwarg_name]
                if 'default' not in arg_kwargs:
                    arg_kwargs['default'] = default_value
                if 'action' not in arg_kwargs and isinstance(default_value, bool):
                    arg_kwargs['action'] = 'store_false' if default_value else 'store_true'

                self._get_argument_group(group).add_argument(*arg_args, **arg_kwargs)
            if varargs:
                group, arg_args, arg_kwargs = self.manual_arguments.get(varargs, ('*', (varargs,), {'nargs': '*'}))
                if 'nargs' not in arg_kwargs:
                    arg_kwargs['nargs'] = '*'
                if 'help' not in arg_kwargs and varargs in task_args_description:
                    arg_kwargs['help'] = task_args_description[varargs]
                self._get_argument_group(group).add_argument(*arg_args, **arg_kwargs)

            self.args = args
            self.kwargs = kwargs
            self.varargs = varargs

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

    def set_group_argument(self, group, *args, **kwargs):
        if args[0].startswith('-'):
            # Optional
            dest = kwargs.get('dest', None)
            if not dest:
                # Find from args
                dest_candidates = [arg for arg in args if arg.startswith('--')]
                if len(dest_candidates):
                    dest = dest_candidates[0].lstrip('-').replace('-', '_')
            if not dest:
                # Raise exception
                raise ValueError('Cannot find destination of the argument "{}" for {}'.format(
                    ', '.join(args),
                    self
                ))
            self.manual_arguments[dest] = (group, args, kwargs)
        else:
            # Positional
            self.manual_arguments[kwargs.get('dest', args[0])] = (group, args, kwargs)

    def set_argument(self, *args, **kwargs):
        self.set_group_argument('*', *args, **kwargs)
