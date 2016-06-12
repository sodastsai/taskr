
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

import argparse
import sys


class DefaultHelpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


class ArgumentTypeError(TypeError):

    def __init__(self, message, parser):
        """
        :type message: str
        :type parser: ArgumentParser
        """
        super(ArgumentTypeError, self).__init__(message)
        self._parser = parser  # type: argparse.ArgumentParser

    def __repr__(self):
        return "{}: error: {}".format(self._parser.prog, str(self))


class ArgumentParser(argparse.ArgumentParser):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("conflict_handler", "resolve")
        kwargs.setdefault("formatter_class", DefaultHelpFormatter)
        super(ArgumentParser, self).__init__(*args, **kwargs)

    def parse_args(self, args=None, namespace=None):
        """
        :type args: tuple[str]
        :type namespace: argparse.Namespace
        :rtype: (dict, tuple[str])
        """
        parsed_namespace, remainders = self.parse_known_args(args=args, namespace=namespace)
        return vars(parsed_namespace), tuple(remainders)

    def error(self, message):
        raise ArgumentTypeError(message, self)
