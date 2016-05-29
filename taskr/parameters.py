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

import inspect
import types

from collections import OrderedDict

import six


# Parameters of Functions ----------------------------------------------------------------------------------------------

@six.python_2_unicode_compatible
class InspectParameter(object):

    @classmethod
    def parameters_of_function(cls, func):
        """
        :type func: function
        :rtype: dict[str, InspectParameter]
        """
        # Get the real function of callable objects
        func_is_function = isinstance(func, types.FunctionType)
        func = func if func_is_function else func.__call__
        # noinspection PyDeprecation
        argspec = inspect.getargspec(func)
        parameters = OrderedDict()

        positional_args_count = len(argspec.args) - len(argspec.defaults or [])
        for positional_arg in argspec.args[:positional_args_count]:
            parameters[positional_arg] = cls(positional_arg, cls.POSITIONAL_OR_KEYWORD)
        for idx, default_args in enumerate(argspec.args[positional_args_count:]):
            parameters[default_args] = cls(default_args, cls.POSITIONAL_OR_KEYWORD, default=argspec.defaults[idx])
        if argspec.varargs:
            parameters[argspec.varargs] = cls(argspec.varargs, cls.VAR_POSITIONAL)
        if argspec.keywords:
            parameters[argspec.keywords] = cls(argspec.keywords, cls.VAR_KEYWORD)

        # Remove the `self` argument if necessary
        if not func_is_function:
            parameters.popitem(last=False)

        return parameters

    POSITIONAL_ONLY = 0
    POSITIONAL_OR_KEYWORD = 1
    VAR_POSITIONAL = 2
    KEYWORD_ONLY = 3
    VAR_KEYWORD = 4

    # noinspection PyPep8Naming
    class empty:
        pass

    def __init__(self, name, kind, default=empty):
        super(InspectParameter, self).__init__()

        if kind not in (self.POSITIONAL_ONLY, self.POSITIONAL_OR_KEYWORD, self.VAR_POSITIONAL,
                        self.KEYWORD_ONLY, self.VAR_KEYWORD):
            raise ValueError("invalid value for 'Parameter.kind' attribute")

        if default is not self.empty:
            if kind in (self.VAR_POSITIONAL, self.VAR_KEYWORD):
                msg = '{} parameters cannot have default values'.format(kind)
                raise ValueError(msg)

        self.name = name
        self.kind = kind
        self.default = default

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, InspectParameter):
            return NotImplemented
        return self.name == other.name and self.kind == other.kind and self.default == other.default

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, self)

    def __str__(self):
        if self.kind == self.POSITIONAL_ONLY:
            return self.name
        elif self.kind == self.POSITIONAL_OR_KEYWORD:
            return "{}={}".format(self.name, self.default)
        elif self.kind == self.VAR_POSITIONAL:
            return "*{}".format(self.name)
        elif self.kind == self.VAR_KEYWORD:
            return "**{}".format(self.name)
        else:
            return ""


if six.PY3:
    ParameterClass = inspect.Parameter
else:
    ParameterClass = InspectParameter


def parameters_of_function(func):
    """
    :type func: function
    :rtype: dict[str, ParameterClass]
    """
    return inspect.signature(func).parameters if six.PY3 else InspectParameter.parameters_of_function(func)
