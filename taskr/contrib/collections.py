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
import copy
import re
import six
if six.PY3:
    from collections.abc import Sequence
else:
    from collections import Sequence

_keypath_index_subscript_pattern = re.compile(r'^\[(?P<index>\d+)\]$')


def _keypath_component_handler(component):
    """

    >>> _keypath_component_handler('str')
    'str'
    >>> _keypath_component_handler('[42]')
    42
    >>> _keypath_component_handler('[label]')
    '[label]'
    >>> _keypath_component_handler('[r1]')
    '[r1]'

    :type component: str
    :rtype: int|str
    """
    match = _keypath_index_subscript_pattern.match(component)
    if match and match.group('index'):
        return int(match.group('index'))
    else:
        return component


def get_value_by_keypath(obj, keypath, **kwargs):
    """

    >>> get_value_by_keypath([1, 2, 3], '[0]')
    1
    >>> get_value_by_keypath({'answer': 42}, 'answer')
    42
    >>> try:
    ...     get_value_by_keypath({'answer': 42}, 'answer.k')
    ... except KeyError as e:
    ...     print(e)
    'answer.k'
    >>> get_value_by_keypath({'answer': 42}, 'answer.k', default='gg')
    'gg'
    >>> get_value_by_keypath({'answer': {'value': 42}}, 'answer.value')
    42
    >>> get_value_by_keypath({'answer': {'value': [41, 42, 43]}}, 'answer.value.[1]')
    42
    >>> try:
    ...     get_value_by_keypath({'answer': {'value': [41, 42, 43]}}, 'answer.value.[3]')
    ... except IndexError as e:
    ...     print(e)
    list index out of range
    >>> get_value_by_keypath({'answer': {'value': [41, 42, 43]}}, 'answer.value.[3]', default='XD')
    'XD'

    :type obj: list[T]|dict[U,T]
    :type keypath: str
    :rtype: T
    """

    if len(keypath) == 0:
        raise KeyError(keypath)

    has_default = 'default' in kwargs
    default = kwargs.get('default')

    target = obj
    for keypath_component in map(_keypath_component_handler, keypath.split('.')):
        if isinstance(target, Sequence) and isinstance(keypath_component, int):
            if keypath_component < len(target) or not has_default:
                target = target[keypath_component]
            else:
                return default
        elif isinstance(target, dict):
            if has_default:
                target = target.get(keypath_component, default)
            else:
                target = target[keypath_component]
        elif has_default:
            return default
        else:
            raise KeyError(keypath)
    return target


def deep_update_dict(dict1, dict2, update_dict1=True):
    """

    >>> expected_dict = {'list': [1, 2, 3, 4], 'answer': 42, 'key': 'value0', 'dict': {'key1': 'value1', \
'key2': 'value2'}, 'set': {1, 3, 4}}
    >>> dict1 = {'answer': 42, 'key': 'value', 'dict': {'key1': 'value1'}, 'list': [1, 2, 3], 'set': {1, 3}}
    >>> dict2 = {'key': 'value0', 'dict': {'key2': 'value2'}, 'list': [3, 4], 'set': {1, 4}}
    >>> dict3 = deep_update_dict(dict1, dict2, update_dict1=False)
    >>> dict1 is dict3
    False
    >>> dict3 == expected_dict
    True
    >>> import copy
    >>> dict4 = copy.deepcopy(dict1)
    >>> dict5 = copy.deepcopy(dict2)
    >>> dict6 = deep_update_dict(dict4, dict5)
    >>> dict4 is dict6
    True
    >>> dict6 == expected_dict
    True


    :type dict1: dict
    :type dict2: dict
    :rtype: dict
    """
    if not update_dict1:
        dict1 = copy.deepcopy(dict1)

    for key, dict2_value in dict2.items():
        if key not in dict1:
            dict1[key] = dict2_value
        else:
            dict1_value = dict1[key]
            if isinstance(dict1_value, list) and isinstance(dict2_value, list):
                seen_items = set()
                dict1[key] = [item for item in (dict1_value + dict2_value) if not (item in seen_items or
                                                                                   seen_items.add(item))]
            elif isinstance(dict1_value, dict) and isinstance(dict2_value, dict):
                dict1[key] = deep_update_dict(dict1_value, dict2_value, update_dict1=update_dict1)
            elif isinstance(dict1_value, set) and isinstance(dict2_value, set):
                dict1[key] = dict1_value | dict2_value
            else:
                dict1[key] = dict2_value
    return dict1
