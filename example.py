#!/usr/bin/env python3
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
from __future__ import unicode_literals, print_function, absolute_import, division
from taskr import task


@task
@task.main
@task.set_group_argument('places', 'source', help='Place where you come from', choices=('Tokyo', 'Osaka'))
@task.set_group_argument('places', 'destination')
@task.set_argument('--speed', help='The speed you wanna run', type=int, dest='speed')
def run(source, destination, vehicle, speed=42, step_size=1):
    """
    Let's travel everywhere

    :param source: Location where you come from
    :param str destination: Place to go
    :param vehicle: The vehicle you wanna take. Maybe `Shinkansen`
    :param speed: The speed how fast you move
    :param step_size: The length of your each step

    yo~

    """
    if speed < 0:
        raise ValueError('speed should be a postive number.')
    print('Run from {0} to {1} by vehicle={4} speed={2} and step={3}'
          .format(source, destination, speed, step_size, vehicle))


@task
@task.pass_argparse_namespace
@task.set_argument('start_time')
@task.set_argument('end_time')
def sleep(arguments):
    print('Sleep from {0.start_time} to {0.end_time}'.format(arguments))


#
# Python 3 only
#
@task
@task.set_name('sum')
@task.set_argument('numbers', type=int)
@task.set_argument('-s', '--start', type=int)
def _sum(*numbers, start=0):
    print(numbers, start)
    print(sum(numbers, start))


if __name__ == '__main__':
    task.dispatch()
