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

import six


def function_args_count(func):
    """
    :type func: function
    :rtype: int
    """
    if six.PY3:
        signature = inspect.signature(func)
        parameters_count = len(signature.parameters)
    else:
        # noinspection PyDeprecation
        argspec = inspect.getargspec(func)
        parameters_count = len(argspec.args)
        if argspec.varargs:
            parameters_count += 1
        if argspec.keywords:
            parameters_count += 1
    return parameters_count
