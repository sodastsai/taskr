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


class Task(object):
    # Argument parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='Action')

    @classmethod
    def dispatch(cls):
        args = cls.parser.parse_args()
        if hasattr(args, '__instance__'):
            kwargs = dict(vars(args))
            del kwargs['__instance__']
            args.__instance__(**kwargs)
        else:
            cls.parser.print_help()

    @classmethod
    def set_argument(cls, *args, **kwargs):
        def wrap(f):
            if not hasattr(f, 'arguments'):
                f.arguments = {}
            f.arguments[args[0]] = (args, kwargs)

            @functools.wraps(f)
            def wrapped(*w_args, **w_kwargs):
                return f(*w_args, **w_kwargs)
            wrapped.original_func = f

            return wrapped

        return wrap

    @classmethod
    def set_name(cls, name):
        def wrap(f):
            f.name = name

            @functools.wraps(f)
            def wrapped(*w_args, **w_kwargs):
                return f(*w_args, **w_kwargs)
            wrapped.original_func = f

            return wrapped

        return wrap

    def __init__(self, func):
        self.function = func
        # Register this task to argparse
        parser = self.subparsers.add_parser(hasattr(func, 'name') and func.name or func.__name__)
        parser.set_defaults(__instance__=self)

        # Get argument spec from original func for setting arguments
        original_func = func
        while hasattr(original_func, 'original_func'):
            original_func = original_func.original_func
        try:
            arg_spec = inspect.getfullargspec(original_func)
        except AttributeError:
            arg_spec = inspect.getargspec(original_func)

        # Parse argument spec into args list and kwargs dict
        if arg_spec.defaults:
            args = arg_spec.args[:-len(arg_spec.defaults)]
            kwargs = dict(zip(arg_spec.args[-len(arg_spec.defaults):], arg_spec.defaults))
        else:
            args = arg_spec.args
            kwargs = {}

        # Setting arguments
        manual_arguments = hasattr(func, 'arguments') and func.arguments or {}
        for arg_name in args:
            if arg_name in manual_arguments:
                arg_args, arg_kwargs = manual_arguments[arg_name]
                parser.add_argument(*arg_args, **arg_kwargs)
            else:
                parser.add_argument(arg_name)
        for kwarg_name, default_value in kwargs.items():
            arg_name = '--' + kwarg_name.replace('_', '-')
            if arg_name in manual_arguments:
                arg_args, arg_kwargs = manual_arguments[arg_name]
                parser.add_argument(*arg_args, **arg_kwargs)
            else:
                parser.add_argument(arg_name, default=default_value)

    def __call__(self, *args, **kwargs):
        self.function(*args, **kwargs)

    @classmethod
    def error(cls, message):
        cls.parser.error(message)

    @classmethod
    def exit(cls, status=0, message=None):
        cls.parser.exit(status, message)
