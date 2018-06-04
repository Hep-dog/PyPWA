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
from typing import Any, Dict, List

from PyPWA import Path, AUTHOR, VERSION

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class BinType(enum.Enum):

    Mass = enum.auto()
    Energy = enum.auto()


class FileSettings(object):

    def __init__(self, settings):
        # type: (Dict[str, str]) -> None
        self.__source_file = Path(settings['source'])
        self.__extra_files = self.__setup_extras(settings['extras'])
        self.__check_files_exist()

    @staticmethod
    def __setup_extras(extras):
        if isinstance(extras, type(None)):
            return list()
        else:
            return [Path(file) for file in extras]

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

    def __init__(self, bin_setting):
        # type: (Dict[str, Any]) -> None
        self.__width = None  # type: float
        self.__bin_type = self.__process_bin_type(bin_setting)
        self.__lower_limit = bin_setting['lower limit']
        self.__upper_limit = bin_setting['upper limit']
        self.__range = self.__upper_limit - self.__lower_limit
        self.__setup_bin_width(bin_setting)

    @staticmethod
    def __process_bin_type(settings):
        # type: (Dict[str, str]) -> BinType
        if settings['binning type'] == "mass":
            return BinType.Mass
        elif settings['binning type'] == 'energy':
            return BinType.Energy
        else:
            raise ValueError(
                'Unknown bin type %s!' % settings['binning type']
            )

    def __setup_bin_width(self, settings):
        # type: (Dict[str, Any]) -> None
        if 'number of bins' in settings:
            self.__calculate_bin_width(settings)
        else:
            self.__width = settings['width of each bin']
            self.__verify_bin_width()

    def __calculate_bin_width(self, settings):
        bin_count = settings['number of bins']
        self.__width = float("%.4f" % (self.__range / bin_count))
        self.__LOGGER.info("Setting bin width to %f" % bin_count)
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

    def get_calculation_prefix(self):
        return {
            BinType.Mass: "_MeV",
            BinType.Energy: "_GeV"
        }[self.__bin_type]

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
    def lower_limits_list(self):
        # type: () -> List(int)
        return list(
            range(self.__lower_limit, self.__upper_limit, self.__width)
        )

    @property
    def bin_count(self):
        # type: () -> int
        return len(self.lower_limits_list)


class SettingsCollection(object):

    def __init__(self, file_settings, bin_settings):
        # type: (FileSettings, List[BinSettings]) -> None
        self.__file_settings = file_settings
        self.__bin_settings = bin_settings

    def get_bin_dimensions(self, dimension):
        if dimension >= self.bin_dimensions_count:
            raise IndexError("The user didn't request that many dimensions!")
        return self.__bin_settings[dimension]

    @property
    def bin_dimensions_count(self):
        # type: () -> int
        return len(self.__bin_settings)

    @property
    def bin_settings(self):
        # type: () -> List[BinSettings]
        return self.__bin_settings

    @property
    def file_settings(self):
        return self.__file_settings


class SettingsFactory(object):

    def __init__(self, settings):
        # type: (Dict[str, Any]) -> None
        self.__bin_settings = list()  # type: List[BinSettings]
        self.__file_settings = list()  # type: List[FileSettings]
        self.__collections = list()  # type: List[SettingsCollection]
        self.__process_bin_settings(settings['bin settings'])
        self.__process_file_settings(settings['files'])
        self.__create_collections()

    def __process_bin_settings(self, bin_settings):
        # type: (List[Dict[str, Any]]) -> None
        for setting in bin_settings:
            self.__bin_settings.append(BinSettings(setting))

    def __process_file_settings(self, file_settings):
        # type: (List[Dict[str, str]]) -> None
        for setting in file_settings:
            self.__file_settings.append(FileSettings(setting))

    def __create_collections(self):
        for file_setting in self.__file_settings:
            self.__collections.append(
                SettingsCollection(file_setting, self.__bin_settings)
            )

    @property
    def collections(self):
        return self.__collections
