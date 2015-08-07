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
import glob
import os
import readline


# Setup readline for path auto-complete
def path_complete(text, state):
    if '~' in text:
        if text == '~':
            text += '/'
        text = os.path.expanduser(text)
    return (glob.glob(text+'*')+[None])[state]

readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(path_complete)


class Color(object):
    CLEAR = -1
    LIGHT = 1
    UNDERLINE = 4
    BLINK = 5
    SWAP = 7
    HIDE = 8

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

    LIGHT_BLACK = 60
    LIGHT_RED = 61
    LIGHT_GREEN = 62
    LIGHT_YELLOW = 63
    LIGHT_BLUE = 64
    LIGHT_MAGENTA = 65
    LIGHT_CYAN = 66
    LIGHT_WHITE = 67

    @classmethod
    def str(cls, message, foreground=-1, background=-1,
            light=False, underline=False, blink=False, swap=False, hide=False):
        codes = []
        if light:
            codes.append(cls.LIGHT)
        if underline:
            codes.append(cls.UNDERLINE)
        if blink:
            codes.append(cls.BLINK)
        if swap:
            codes.append(cls.SWAP)
        if hide:
            codes.append(cls.HIDE)
        if foreground >= 0:
            codes.append(cls.FOREGROUND + foreground)
        if background >= 0:
            codes.append(cls.BACKGROUND + background)

        return cls.str_with_codes(message, *codes)

    @classmethod
    def str_with_codes(cls, message, *codes):
        return '{}{}{}'.format(cls.code(*codes), message, cls.code())

    @classmethod
    def code(cls, *codes):
        return '\033[{}m'.format(';'.join(map(str, codes)))


class Console(object):

    error_prefix = '[x]  '
    error_color = (Color.RED, False)

    success_prefix = '[v]  '
    success_color = (Color.GREEN, False)

    info_prefix = '[i]  '
    info_color = (Color.CYAN, False)

    prompt_prefix = '[?]  '
    prompt_color = (Color.MAGENTA, False)

    highlight_prefix = '[:]  '
    highlight_color = (Color.CYAN, True)

    warn_prefix = '[!!] '
    warn_color = (Color.YELLOW, False)

    def __init__(self, f, write_line=True, color=True):
        self.output_color = color
        self._output = f
        self._write_line = write_line

    def __getattr__(self, name):
        if name.endswith('_color') or name.endswith('_prefix'):
            raise AttributeError("'{0}' object has no attribute '{1}'".format(self.__class__.__name__, name))

        color, light = getattr(self, '{0}_color'.format(name), (Color.CLEAR, False))
        prefix = getattr(self, '{0}_prefix'.format(name), '')

        def func(message, bar_width=0, bar_character='='):
            self.show('{0}{1}'.format(prefix, message),
                      foreground=color, light=light, bar_width=bar_width, bar_character=bar_character)
        return func

    def show(self, message, foreground=-1, background=-1, light=False, bar_width=0, bar_character='='):
        if bar_width != 0:
            message = self.bar(message, bar_width, bar_character)
        output_str = Color.str(message, foreground, background, light) if self.output_color else message
        if self._write_line:
            output_str += '\n'
        self._output.write(output_str)

    @staticmethod
    def bar(message, width=120, character='='):
        if message:
            message += ' '
        return message + character * (width - (len(message) + 1))

    def input(self, prompt,
              hint=None, validators=None, repeat_until_valid=False, task=None, leave_when_cancel=None, **kwargs):
        """
        :param default:
        """
        has_default = 'default' in kwargs
        default = kwargs.get('default', None)

        leave_when_cancel = leave_when_cancel or bool(task)

        message_components = [prompt, ' ']
        if hint is not None:
            message_components.append('({0})'.format(hint))
        if has_default:
            message_components.append('[{0}]'.format(default))
        message = ''.join(message_components).strip() + ': '

        import six
        # noinspection PyShadowingBuiltins
        input = six.moves.input
        while True:
            has_result = True
            try:
                result = input(message).strip()
            except KeyboardInterrupt:
                self.show('')
                error_msg = 'User cancelled input.'
                self.error(error_msg)
                if task and leave_when_cancel:
                    task.exit(1)
                result = None
            finally:
                # Default value
                if (result is None or len(result) == 0) and has_default:
                    result = default
                # Validate
                if validators:
                    for validator in validators:
                        try:
                            result = validator(result)
                        except ValueError as e:
                            has_result = False
                            if has_default:
                                result = default
                            else:
                                self.error(str(e))
                            break
                # Return rt repeat
                if not repeat_until_valid or has_result:
                    return result
