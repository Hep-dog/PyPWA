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

"""

import enum
from typing import List, Optional as Opt

import numpy

from PyPWA import Path, AUTHOR, VERSION

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class BinType(enum.Enum):

    Mass = enum.auto()
    Energy = enum.auto()


def get_calculation_prefix(binning_type):
    return {
        BinType.Mass: "MeV",
        BinType.Energy: "GeV"
    }[binning_type]


class FileSettings(object):

    def __init__(self, source, extras):
        # type: (Path, List[Path]) -> None
        self.__source_file = source
        self.__extra_files = extras
        self.__check_files_exist()

    def __check_files_exist(self):
        self.__raise_if_file_does_not_exist(self.__source_file)
        self.__iterate_over_multiple_files(self.__extra_files)

    @staticmethod
    def __raise_if_file_does_not_exist(file):
        # type: (Path) -> None
        if not file.is_file():
            raise ValueError("%s does not exist!" % file)

    def __iterate_over_multiple_files(self, files):
        # type: (List[Path]) -> None
        for file in files:
            self.__raise_if_file_does_not_exist(file)

    @property
    def source_file(self):
        # type: () -> Path
        return self.__source_file

    @property
    def extra_files(self):
        # type: () -> List[Path]
        return self.__extra_files


class BinSettings(object):

    def __init__(self, bin_type, lower_limit, upper_limit, width):
        # type: (str, int, int, int, Opt[bool]) -> None
        self.__bin_type = bin_type
        self.__lower_limit = lower_limit
        self.__upper_limit = upper_limit
        self.__width = width

    @property
    def bin_type(self):
        return self.__bin_type

    @property
    def lower_limit(self):
        return self.__lower_limit

    @property
    def upper_limit(self):
        return self.__upper_limit

    @property
    def width(self):
        return self.__width
