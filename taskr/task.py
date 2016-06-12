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

from .decorators.once import oncemethod
from .parameters import parameters_of_function, ParameterClass


@six.python_2_unicode_compatible
class Task(object):

    def __init__(self, callable_obj, task_manager):
        """
        :type callable_obj: callable
        :type task_manager: taskr.task_manager.TaskManager
        """
        self.callable = callable_obj
        functools.update_wrapper(self, self.callable)
        self.name = self.callable.__name__.replace("_", "-").lower()

        self.task_manager = task_manager

        # Parse default registered arguments from the callable object
        self.has_var_keyword = False
        self.has_var_positional = False
        self._argparser_finalized = False
        self.registered_arguments = OrderedDict()
        """:type : dict[str, tuple]"""
        for arg_name, parameter in self.callable_parameters.items():
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
        parser = self.task_manager.task_subparser.add_parser(self.name)
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

        for group, add_args, add_kwargs in self.registered_arguments.values():
            parser = parsers_groups.setdefault(group, create_argument_group(group))  # type: argparse.ArgumentParser
            parser.add_argument(*add_args, **add_kwargs)

    # Parameters

    @property
    @oncemethod("_callable_parameters")
    def callable_parameters(self):
        return parameters_of_function(self.callable)

    @property
    @oncemethod("_positional_parameters")
    def positional_parameters(self):
        return [parameter for parameter in self.callable_parameters.values()
                if parameter.kind == ParameterClass.POSITIONAL_OR_KEYWORD and
                parameter.default == ParameterClass.empty]

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
        if not self.has_var_keyword and dest not in self.callable_parameters:
            raise ValueError("\"{}\" is not allowed to be added as an argument of {}."
                             " {} doesn't accept extra keyword args.".format(dest, self.name, self.name))
        self.registered_arguments[dest] = (group, args, kwargs)

    def set_argument(self, *args, **kwargs):
        self.set_group_argument('*', *args, **kwargs)
