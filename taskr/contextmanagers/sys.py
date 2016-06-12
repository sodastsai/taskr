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

import sys
from contextlib import contextmanager

import six


@contextmanager
def replace_argv(new_argv):
    """
    :type new_argv: tuple[str]
    """
    original_argv = sys.argv
    sys.argv = new_argv
    try:
        yield
    finally:
        sys.argv = original_argv


class CapturedStdioResult(object):

    def __init__(self):
        super(CapturedStdioResult, self).__init__()
        self._captured_stdout = None  # type: str
        self._captured_stderr = None  # type: str
        self._finalized = False

    @property
    def captured_stdout(self):
        assert self._finalized, "This captured stdio result is not finalized."
        return self._captured_stdout

    @property
    def captured_stderr(self):
        assert self._finalized, "This captured stdio result is not finalized."
        return self._captured_stderr


@contextmanager
def capture_stdio():
    """
    :rtype: collections.Generator[CapturedStdioResult]
    """
    sys.stdout = six.StringIO()
    sys.stderr = six.StringIO()

    result = CapturedStdioResult()
    try:
        yield result
    finally:
        result._captured_stdout = sys.stdout.getvalue()
        result._captured_stderr = sys.stderr.getvalue()
        result._finalized = True
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
