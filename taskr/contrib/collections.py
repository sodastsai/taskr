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
