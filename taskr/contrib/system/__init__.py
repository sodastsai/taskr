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
import six


class _OSInfo(object):

    @property
    def is_osx(self):
        return sys.platform.lower() == 'darwin'

    @property
    def is_linux(self):
        return sys.platform.startswith('linux')

os_info = _OSInfo()


class RunCommandError(ValueError):
    pass


_run_global_settings = {
    'capture_output': True,
    'use_shell': False,
    'print_command': False,
    'should_return_returncode': False,
    'should_raise_when_fail': False,
    'should_strip_output': True
}


def _process_run_command_output(raw_output, strip_output):
    if raw_output is None:
        return raw_output

    try:
        _output = raw_output.decode('utf-8')
    except ValueError:
        return raw_output
    else:
        return _output[:-1] if strip_output else _output  # strip last '\n'


def run_settings(**kwargs):
    """
    :type capture_output: bool
    :type use_shell: bool
    :type print_command: bool
    :type should_return_returncode: bool
    :type should_raise_when_fail: bool
    :type should_strip_output: bool
    """
    _run_global_settings.update(kwargs)


def run(command, **kwargs):
    """
    :type command: str
    :type capture_output: bool
    :type use_shell: bool
    :type print_command: bool
    :type should_return_returncode: bool
    :type should_raise_when_fail: bool
    :type should_strip_output: bool
    :rtype: (str, str, int) | (str, str)
    """
    for key, value in six.iteritems(_run_global_settings):
        kwargs.setdefault(key, value)
    capture_output = kwargs['capture_output']
    use_shell = kwargs['use_shell']
    print_command = kwargs['print_command']
    should_return_returncode = kwargs['should_return_returncode']
    should_raise_when_fail = kwargs['should_raise_when_fail']
    should_strip_output = kwargs['should_strip_output']

    use_shell = '&&' in command or '||' in command or use_shell
    if print_command:
        print(command)
    popen = subprocess.Popen(command if use_shell else shlex.split(command),
                             stdout=subprocess.PIPE if capture_output else None,
                             stderr=subprocess.PIPE if capture_output else None,
                             shell=use_shell)

    stdout, stderr = popen.communicate()
    return_code = popen.returncode
    if return_code != 0 and should_raise_when_fail:
        raise RunCommandError('Command execution returns {}'.format(return_code))

    if capture_output:
        stdout = _process_run_command_output(stdout, should_strip_output)
        stderr = _process_run_command_output(stderr, should_strip_output)

        if should_return_returncode:
            return stdout, stderr, return_code
        else:
            return stdout, stderr
    elif should_return_returncode:
        return return_code


def has_command(command):
    """
    test wheather a command exists in current $PATH or not.
    :type command: str
    :rtype: bool
    """
    stdout, _, return_code = run('which {}'.format(command), should_return_returncode=True)
    return len(stdout) != 0 and return_code == 0
