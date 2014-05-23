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


class Console(object):
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

    @classmethod
    def color_str(cls, message, foreground=-1, background=-1, light=False):
        codes = []
        if light:
            codes.append(str(cls.LIGHT))
        if foreground >= 0:
            codes.append(str(cls.FOREGROUND + foreground))
        if background >= 0:
            codes.append(str(cls.BACKGROUND + background))
        return '\033[{0}m{1}\033[m'.format(';'.join(codes), message)

    @classmethod
    def error(cls, message):
        print(cls.color_str('😱  {0}'.format(message), cls.RED))

    @classmethod
    def success(cls, message):
        print(cls.color_str('🍺  {0}'.format(message), cls.GREEN))

    @classmethod
    def info(cls, message):
        print(cls.color_str('✈️  {0}'.format(message), cls.CYAN))

    @classmethod
    def prompt(cls, message):
        print(cls.color_str('👻  {0}'.format(message), cls.MAGENTA))

    @classmethod
    def highlight(cls, message):
        print(cls.color_str('🚬  {0}'.format(message), cls.CYAN, light=True))

    @classmethod
    def show(cls, message, foreground=-1, background=-1, light=False):
        print(cls.color_str(message, foreground, background, light))
