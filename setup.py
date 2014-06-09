#!/usr/bin/env python

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

from setuptools import setup, find_packages
import os
import taskr

with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as f:
    long_description = f.read()

setup(name='taskr',
      version=taskr.__version__,
      description='Python Command Line Utility',
      author='sodastsai',
      author_email='sodas2002@gmail.com',
      license='Apache License Version 2.0',
      url='https://github.com/sodastsai/taskr',
      package_data={'': ['license.txt', 'README.md']},
      long_description=long_description,
      packages=find_packages())
