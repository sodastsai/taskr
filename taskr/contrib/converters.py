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