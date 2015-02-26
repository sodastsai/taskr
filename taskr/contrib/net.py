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
import json
import six


def get_ip():
    """
    :rtype: str
    """
    urlopen = six.moves.urllib.request.urlopen
    # noinspection PyPep8Naming
    URLError = six.moves.urllib.error.URLError
    try:
        return json.loads(urlopen('http://httpbin.org/ip').read().decode('utf-8'))['origin']
    except (ValueError, KeyError, URLError):
        return None


def network_available():
    """
    :rtype: bool
    """
    return get_ip() is not None
