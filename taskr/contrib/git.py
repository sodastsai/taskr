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

class GitRepo(object):

    def __init__(self, source_root):
        self._source_root = source_root
        """:type: str"""

    @property
    def source_root(self):
        return self._source_root

    def _run_git_command(self, command, capture_output=True, use_shell=False):
        """
        :type command: str
        :type capture_output: bool
        :type use_shell: bool
        :rtype: str
        """
        stdout, stderr = run('cd {} && {}'.format(self.source_root, command),
                             capture_output=capture_output, use_shell=use_shell)
        if stderr:
            raise ValueError('"{}" is not a git repository'.format(self.source_root))
        return stdout

    @property
    def is_clean(self):
        """
        :rtype: bool
        """
        return len(self.status) == 0

    @property
    def status(self):
        """
        :rtype: OrderedDict[str, str]
        """
        result = OrderedDict()
        for stdout_line in self._run_git_command('git status --porcelain').split('\n'):
            if stdout_line:
                result[stdout_line[2:].strip()] = stdout_line[:2]
        return result

    @property
    def current_branch(self):
        """
        :rtype: str
        """
        return self._run_git_command('git branch | grep "*" | awk \'{print $2}\'')
