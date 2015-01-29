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
import shlex
import subprocess
import sys


class _OSInfo(object):

    @property
    def is_osx(self):
        return sys.platform.lower() == 'darwin'

    @property
    def is_linux(self):
        return sys.platform.startswith('linux')

os_info = _OSInfo()


def run(command, capture_output=True, use_shell=False):
    """
    :type command: str
    :type capture_output: bool
    :type use_shell: bool
    :rtype: (str, str)
    """
    use_shell = '&&' in command or '||' in command or use_shell
    stdout, stderr = subprocess.Popen(command if use_shell else shlex.split(command),
                                      stdout=subprocess.PIPE if capture_output else None,
                                      stderr=subprocess.PIPE if capture_output else None,
                                      shell=use_shell).communicate()
    return stdout.decode('utf-8').strip(), stderr.decode('utf-8').strip()


def has_command(command):
    """
    test wheather a command exists in current $PATH or not.
    :type command: str
    :rtype: bool
    """
    stdout, _ = run('which {}'.format(command))
    return len(stdout) != 0
