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
from collections import OrderedDict
from .system import run


# Ref: http://stackoverflow.com/questions/2657935/checking-for-a-dirty-index-or-untracked-files-with-git
# Ref: https://www.kernel.org/pub/software/scm/git/docs/git-status.html

def is_clean(source_root):
    """
    :type source_root: str
    :rtype: bool
    """
    return len(status(source_root)) == 0


def status(source_root):
    """
    :type source_root: str
    :rtype: OrderedDict[str, str]
    """
    stdout, stderr = run('cd {} && git status --porcelain'.format(source_root))
    if stderr:
        raise ValueError('"{}" is not a git repository'.format(source_root))
    result = OrderedDict()
    for stdout_line in stdout.split('\n'):
        if stdout_line:
            result[stdout_line[2:].strip()] = stdout_line[:2]
    return result
