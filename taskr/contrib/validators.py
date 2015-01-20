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
import os
import re


def custom_message_validator(validator, error_message=None):
    def _validator(raw_value):
        exception = None
        try:
            value = validator(raw_value)
        except ValueError as e:
            value = None
            exception = e
        if value:
            return value
        else:
            raise ValueError(error_message) if error_message else exception
    return _validator


def integer_validator(error_message=None):
    return custom_message_validator(int, error_message=error_message)


def float_validator(error_message=None):
    return custom_message_validator(float, error_message=error_message)


def boolean_function_validator(func):
    def _validator(raw_value):
        if func(raw_value):
            return raw_value
        else:
            raise ValueError('Validator returns false.')
    return _validator


def validate_boolean(raw_value):
    import six
    if isinstance(raw_value, six.string_types):
        if raw_value.lower() in ('true', 't', 'yes', 'y'):
            return True
        elif raw_value.lower() in ('false', 'f', 'no', 'n'):
            return False
        else:
            raise ValueError('Choose yes or no')
    elif isinstance(raw_value, (int, float)):
        return bool(raw_value)
    else:
        raise ValueError('Unknown input value type')


def filepath_validator(is_directory=False):
    def validator(filepath):
        if not (os.path.isdir if is_directory else os.path.exists)(os.path.abspath(filepath)):
            raise ValueError('No file exists at {0}'.format(filepath))
        return filepath
    return validator


def regex_validator(pattern):
    import six
    def validator(value):
        if not bool(re.search(pattern, value)):
            raise ValueError('{0} cannot match pattern {1}'.format(
                value,
                pattern if isinstance(pattern, six.string_types) else pattern.pattern))
        return value
    return validator


def number_pair_validator(number_type, length=None, delimiter=','):
    def validator(raw_value):
        pairs = list(map(number_type, raw_value.split(delimiter)))
        if length is not None and len(pairs) != length:
            raise ValueError('The number of items in the pair is incorrect.')
        return pairs
    return validator