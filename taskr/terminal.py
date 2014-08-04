# -*- encoding: utf-8 -*-

#
# Copyright 2014 sodastsai
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


class Color(object):
    LIGHT = 1
    FOREGROUND = 30
    BACKGROUND = 40
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7
    CLEAR=-1

    @classmethod
    def str(self, message, foreground=-1, background=-1, light=False):
        codes = []
        if light:
            codes.append(str(self.LIGHT))
        if foreground >= 0:
            codes.append(str(self.FOREGROUND + foreground))
        if background >= 0:
            codes.append(str(self.BACKGROUND + background))
        return '\033[{0}m{1}\033[m'.format(';'.join(codes), message)


class Console(object):

    error_prefix = '😱'
    error_color = (Color.RED, False)

    success_prefix = '🍺'
    success_color = (Color.GREEN, False)

    info_prefix = '✈️'
    info_color = (Color.CYAN, False)

    prompt_prefix = '👻'
    prompt_color = (Color.MAGENTA, False)

    highlight_prefix = '🚬'
    highlight_color = (Color.CYAN, True)

    def __init__(self, f, write_line=True):
        self._output = f
        self._write_line = write_line

    def __getattr__(self, name):
        if name.endswith('_color') or name.endswith('_prefix'):
            raise AttributeError("'{0}' object has no attribute '{1}'".format(self.__class__.__name__, name))

        color, light = getattr(self, '{0}_color'.format(name), (Color.CLEAR, False))

        prefix = getattr(self, '{0}_prefix'.format(name), '')
        if len(prefix)!=0:
            prefix += '  '

        def func(message, bar_width=0, bar_character='='):
            self.show('{0}{1}'.format(prefix, message),
                foreground=color, light=light, bar_width=bar_width, bar_character=bar_character)
        return func

    def show(self, message, foreground=-1, background=-1, light=False, bar_width=0, bar_character='='):
        if bar_width != 0:
            message = self.bar(message, bar_width, bar_character)
        output_str = Color.str(message, foreground, background, light)
        if self._write_line:
            output_str += '\n'
        self._output.write(output_str)

    @staticmethod
    def bar(message, width=120, character='='):
        return message + ' ' + character * (width - (len(message) + 1))
