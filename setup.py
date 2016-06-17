#!/usr/bin/env python

#
# Copyright 2014-2016 sodastsai
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

from setuptools import setup, find_packages

setup(name='taskr',
      version='0.3.0',
      description='Python Command Line Utility',
      author='sodastsai',
      author_email='sodas2002@gmail.com',
      license='Apache License Version 2.0',
      url='https://github.com/sodastsai/taskr',
      long_description='''taskr - python command line utility helper''',
      packages=find_packages(),
      test_suite="tests",
      install_requires=[
          'six>=1.10.0',
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX :: Linux',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Software Development',
          'Topic :: Utilities',
      ])
