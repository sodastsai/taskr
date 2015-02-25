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
from ..system import run


def mdfind(**kwargs):
    """
    :rtype: (str, str)
    """
    return run('mdfind \'{}\''.format(' && '.join(['{}=="{}"'.format(key, value) for key, value in kwargs.items()])),
               capture_output=True)


def app_path(app_name):
    """
    :type app_name: str
    :rtype: [str]
    """
    stdout, _ = mdfind(kMDItemKind='Application', kMDItemDisplayName=app_name)
    return stdout.splitlines()


def has_app(app_name):
    """
    :type app_name: str
    :rtype: bool
    """
    return len(app_path(app_name)) != 0
