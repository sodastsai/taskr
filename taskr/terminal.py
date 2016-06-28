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

# noinspection PyCompatibility
from enum import IntEnum

import six


# ANSI Escape Code -----------------------------------------------------------------------------------------------------

class ANSIEscapeCode(IntEnum):
    clear = -1
    none = 0
    light = 1
    underline = 4
    blink = 5
    swap = 7
    hide = 8

    fBlack = 30
    fRed = 31
    fGreen = 32
    fYellow = 33
    fBlue = 34
    fMagenta = 35
    fCyan = 36
    fWhite = 37

    bBlack = 40
    bRed = 41
    bGreen = 42
    bYellow = 43
    bBlue = 44
    bMagenta = 45
    bCyan = 46
    bWhite = 47

    @staticmethod
    def to_string(*codes):
        """
        :type codes: collections.Iterable[ANSIEscapeCode]
        :rtype: str
        """
        return '\033[{}m'.format(';'.join(six.text_type(code.value) for code in codes))


class ANSIEscapedString(object):

    def __init__(self, string, *codes):
        """
        :type string: str
        :type codes: collections.Iterable[ANSIEscapeCode]
        """
        self.string = string
        self.codes = codes

    def __str__(self):
        return "{}{}{}".format(
            ANSIEscapeCode.to_string(*self.codes),
            self.string,
            ANSIEscapeCode.to_string(ANSIEscapeCode.none)
        )
