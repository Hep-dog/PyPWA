#  coding=utf-8
#
#  PyPWA, a scientific analysis toolkit.
#  Copyright (C) 2016 JLab
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Simple masking utility for PyPWA.
---------------------------------
This is an argument based program that supports both masking of any defined
data type, while also supporting converting of data from one data format to
another.
"""

from PyPWA import AUTHOR, VERSION
from PyPWA.initializers.arguments import arguments_options
from PyPWA.progs.masking import masking

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class MaskingArguments(arguments_options.Main):

    _NAME = "masking utility"
    _REQUIRED = ["Builtin Parser", "Builtin Iterator"]

    def _add_arguments(self):
        self.__add_input_argument()
        self.__add_masking_argument()
        self.__add_and_argument()
        self.__add_or_argument()
        self.__add_xor_argument()
        self.__add_output_file()

    def __add_input_argument(self):
        self._parser.add_argument(
            "--input", "-i", type=str, required=True, help="Input file"
        )

    def __add_masking_argument(self):
        self._parser.add_argument(
            "--mask", "-m", type=str, action="append", help="Masking file"
        )

    def __add_and_argument(self):
        self._parser.add_argument(
            "--and-masks", action="store_true", default=True,
            help="AND mask files together (DEFAULT)"
        )

    def __add_or_argument(self):
        self._parser.add_argument(
            "--or-masks", action="store_true", default=False,
            help="OR mask files together."
        )

    def __add_xor_argument(self):
        self._parser.add_argument(
            "--xor-masks", action="store_true", default=False,
            help="XOR mask files together."
        )

    def __add_output_file(self):
        self._parser.add_argument(
            "--output", "-o", type=str, required=True, help="Output file"
        )

    def get_interface(self, namespace, plugins):
        mask_type = self.__setup_mask_type(namespace)
        return masking.Masking(
            namespace.input, namespace.output, plugins['Builtin Parser'],
            plugins['Builtin Iterator'], namespace.mask, mask_type
        )

    @staticmethod
    def __setup_mask_type(namespace):
        if namespace.xor_masks and namespace.or_masks:
            raise ValueError("Can't use XOR and OR!")
        elif namespace.xor_masks:
            return masking.MaskType.XOR
        elif namespace.or_masks:
            return masking.MaskType.OR
        else:
            return masking.MaskType.AND
