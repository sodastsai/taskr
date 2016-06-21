#
# Copyright 2014-2016 sodastsai
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

from __future__ import absolute_import, division, print_function, unicode_literals

import six


def to_string(iterable, threshold=-1, item="item", item_plural="items"):
    """
    Convert an iterable to human-readable string representation.

    Example:
    >>> to_string(range(2))
    '0 and 1'
    >>> to_string(range(3))
    '0, 1, and 2'
    >>> to_string(range(8), threshold=3)
    '0, 1, 2, and 5 items'
    >>> to_string(range(8), threshold=3, item="number", item_plural="numbers")
    '0, 1, 2, and 5 numbers'

    :param collections.Iterable iterable: The iterable which you want to convert to string representation
    :param int threshold: The number of items you want to show before "and".
    :param str|unicode item: The signular unit term for the items of the iterable, "item" by default.
    :param str|unicode item_plural: The plural unit term for the items of the iterable, "items" by default.
    :return str|unicode: The concatented string representation of the iterator
    """
    iterable_list = list(iterable)
    # Find threshold
    if threshold < 0 or threshold >= len(iterable_list):
        threshold = len(iterable_list)
    # Populate items
    items = [six.text_type(iterable_content) for iterable_content in iterable_list[:threshold]]
    # Count remainder items
    remainder_length = max(len(iterable_list) - threshold, 0) if threshold >= 0 else 0
    if remainder_length > 0:
        items.append("{} {}".format(remainder_length, item_plural if remainder_length > 1 else item))
    # Join items
    item_list_length = len(items)
    if item_list_length >= 2:
        return ", ".join(items[:-1]) + ("," if item_list_length > 2 else "") + " and " + items[-1]
    elif item_list_length == 1:
        return items[0]
    else:
        return ""
