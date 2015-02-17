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

import functools
from importlib import import_module


def lazy_property(func):
    """
    >>> def add(i, j):
    ...     print('add called')
    ...     return i + j
    ...
    >>> class K(object):
    ...
    ...     @lazy_property
    ...     def lazy_number(self):
    ...         return add(1, 1)
    ...
    ...     @property
    ...     def number(self):
    ...         return add(1, 1)
    ...
    >>> k = K()
    >>> k.lazy_number
    add called
    2
    >>> k.lazy_number
    2
    >>> k.number
    add called
    2
    >>> k.number
    add called
    2

    :param func: types.FunctionType
    :return: types.FunctionType
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        instance = args[0]
        member_name = '_{}_taskr_lazy_property'.format(func.__name__)
        result = getattr(instance, member_name, None)
        if not result:
            result = func(*args, **kwargs)
            setattr(instance, member_name, result)
        return result
    return property(wrapper)


def import_string(symbol_path):
    symbol_components = symbol_path.split('.')
    symbol = symbol_components[-1]
    symbol_module = '.'.join(symbol_components[:-1])
    return getattr(import_module(symbol_module), symbol)
