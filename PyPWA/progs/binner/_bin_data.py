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
import logging
import warnings
from typing import Tuple, List, Optional as Opt

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

    __LOGGER = logging.getLogger(__name__ + ".BinSettings")

    def __init__(
            self, bin_type, lower_limit, upper_limit, width, use_numbers):
        # type: (BinType, int, int, int, Opt[bool]) -> None
        self.__bin_type = bin_type
        self.__lower_limit = lower_limit
        self.__upper_limit = upper_limit
        self.__range = upper_limit - lower_limit
        self.__width = width
        self.__setup_bin_settings(use_numbers)

    def __setup_bin_settings(self, use_numbers):
        # type: (bool) -> None
        if use_numbers:
            self.__calculate_bin_width()
        else:
            self.__verify_bin_width()

    def __calculate_bin_width(self):
        self.__width = float("%.4f" % (self.__range / self.__width))
        self.__LOGGER.info("Settings bin width to %f" % self.__width)
        self.__verify_bin_width()

    def __verify_bin_width(self):
        bin_count = int(self.__range / self.__width)
        calculated_upper = self.__lower_limit + (bin_count * self.__width)
        if not calculated_upper == self.__upper_limit:
            self.__throw_warning(calculated_upper)
            self.__upper_limit = calculated_upper

    def __throw_warning(self, calculated_upper_limit):
        # type: (float) -> None
        warning_string = (
            "Bin Width %f doesn't divide evenly into limits: %f, %f; "
            "Setting upper limit to %f!" % (
                self.__width, self.__lower_limit, self.__upper_limit,
                calculated_upper_limit
            )
        )
        warnings.warn(warning_string, UserWarning)

    @property
    def bin_type(self):
        # type: () -> BinType
        return self.__bin_type

    @property
    def lower_limit(self):
        # type: () -> float
        return self.__lower_limit

    @property
    def upper_limit(self):
        # type: () -> float
        return self.__upper_limit

    @property
    def width(self):
        # type: () -> float
        return self.__width

    @property
    def lower_limits_tuple(self):
        # type: () -> Tuple(int)
        return tuple(
            range(self.__lower_limit, self.__upper_limit, self.__width)
        )

    @property
    def bin_count(self):
        # type: () -> int
        return len(self.lower_limits_tuple)


class SettingsCollection(object):

    def __init__(self, file_settings, bin_settings):
        # type: (FileSettings, Tuple[BinSettings]) -> None
        self.__file_settings = file_settings
        self.__bin_settings = bin_settings

    def get_bin_dimensions(self, dimension):
        if dimension >= self.bin_dimensions_count:
            raise IndexError("The user didn't request that many dimensions!")
        return self.__bin_settings[dimension]

    @property
    def bin_dimensions_count(self):
        return len(self.__bin_settings)

    @property
    def bin_settings(self):
        return self.__bin_settings
