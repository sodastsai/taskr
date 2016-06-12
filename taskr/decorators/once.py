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

import functools

import six


def once(once_key=None, is_method=False):
    def decorator(func):
        @six.wraps(func)
        def wrapper(*args, **kwargs):
            result_attr = once_key or "_{}_taskr_once_result".format(getattr(func, "__name__", func))
            target = args[0] if is_method else func
            if not hasattr(target, result_attr):
                setattr(target, result_attr, func(*args, **kwargs))
            return getattr(target, result_attr)
        return wrapper
    return decorator


oncemethod = functools.partial(once, is_method=True)
