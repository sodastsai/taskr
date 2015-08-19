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
from __future__ import unicode_literals, division, absolute_import, print_function
import re


def number(val):
    float_val = float(val)
    int_val = int(float_val)
    return int_val if int_val == float_val else float_val


_underscore_prefix_letter_pattern = re.compile(r'_([a-z])')


def camelcase(snakecase_string, capitalize_head=False):
    """
    :type snakecase_string: str
    :rtype: str
    """
    result = _underscore_prefix_letter_pattern.sub(lambda x: x.group(1).upper(), snakecase_string)
    if capitalize_head:
        result = result[0].upper() + result[1:]
    return result


_uppercase_letter_pattern = re.compile(r'([A-Z])')


def snakecase(camelcase_string):
    """
    :type camelcase_string: str
    :rtype: str
    """
    return _uppercase_letter_pattern.sub(lambda x: ('_' if x.start() else '') + x.group(0), camelcase_string).lower()


_quote_pattern = re.compile(r'(["\'])', flags=re.MULTILINE)
_escaped_quote_pattern = re.compile(r'\\(["\'])', flags=re.MULTILINE)


def escape_quote(string):
    """
    :type string: str
    :rtype: str
    """
    return _quote_pattern.sub(r'\\\g<1>', string)


def unescape_quote(string):
    """
    :type string: str
    :rtype: str
    """
    return _escaped_quote_pattern.sub(r'\g<1>', string)


def collections_to_string(iterable, threshold=-1):
    """

    >>> collections_to_string([])
    ''
    >>> collections_to_string([1])
    '1'
    >>> collections_to_string([1, 2])
    '1 and 2'
    >>> collections_to_string([1, 2, 3, 4])
    '1, 2, 3, and 4'
    >>> collections_to_string([1, 2, 3, 4], threshold=4)
    '1, 2, 3, and 4'
    >>> collections_to_string([1, 2, 3, 4, 5, 6], threshold=4)
    '1, 2, 3, 4, and 2 items'
    >>> collections_to_string([1, 2, 3, 4, 5], threshold=4)
    '1, 2, 3, 4, and 5'
    >>> collections_to_string([1, 2, 3, 4], threshold=20)
    '1, 2, 3, and 4'

    """
    if len(iterable) == 0:
        return ''
    elif len(iterable) < 2:
        return str(iterable[0])

    if threshold == -1 or threshold >= len(iterable):
        threshold = len(iterable) - 1

    comman_list = []
    and_item = None
    for idx, item in enumerate(iterable):
        if and_item is not None:
            break
        elif len(comman_list) < threshold:
            comman_list.append(item)
        elif idx == len(iterable) - 1:
            and_item = item
        else:
            remainder_length = len(iterable) - idx
            and_item = '{} items'.format(remainder_length)

    return ', '.join(map(str, comman_list)) + (',' if len(comman_list) > 2 else '') + ' and ' + str(and_item)
