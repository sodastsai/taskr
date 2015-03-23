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
import math
from taskr import console as default_console
from taskr.contrib.validators import integer_validator


def prompt_for_choice(choices, prompt=None, console=default_console, default=-1):
    """
    :param choices: list of choices. should be a list of str
    :type choices: list[str]
    :param prompt: the prompt to be shown while asking user. default is 'choose one from above options'
    :type prompt: str
    :param console: console used to output
    :type console: taskr.terminal.Console
    :param default: default option of these choice. any value less than 0 means no default value
    :type default: int
    :return: the value use choose, or the default one
    :rtype: int
    """
    assert default < len(choices), 'Default option is great than the number of choices'
    has_default = default >= 0

    # Show options
    zero_paddings = int(math.ceil(math.log10(len(choices))))
    choice_template = '{{}}{{:{}d}}) {{}}'.format(zero_paddings)
    if has_default:
        default_prefix = '* '
        non_default_prefix = '  '
    else:
        default_prefix = non_default_prefix = ''

    for i, choice in enumerate(choices):
        console.show(choice_template.format(default_prefix if i == default else non_default_prefix, i, choice))

    # Ask
    def choice_validator(value):
        if value < len(choices):
            return value
        else:
            raise ValueError('The index is greater than the number of choices')

    input_kwargs = {}
    if has_default:
        input_kwargs['default'] = default
    return console.input(prompt=prompt or 'Choose one from above options',
                         validators=[integer_validator(error_message='Choose a number'),
                                     choice_validator],
                         repeat_until_valid=True,
                         **input_kwargs)


if __name__ == '__main__':
    cities = ['Tokyo', 'Osaka', 'Sapporo', 'Nagoya']
    print(cities[prompt_for_choice(cities, prompt='Choose a city', default=0)])
    print('-'*40)
    print(cities[prompt_for_choice(cities, prompt='Choose a city')])
