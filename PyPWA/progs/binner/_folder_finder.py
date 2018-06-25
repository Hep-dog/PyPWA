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

from typing import List

from PyPWA import AUTHOR, VERSION
from PyPWA.progs.binner import _settings_parser

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class _GetBinIndex(object):

    def __init__(self, limits, width):
        self.__limits = limits
        self.__width = width

    def get_bin_id(self, calculated_value):
        if calculated_value < self.__limits[0]:
            return 'underflow'
        else:
            return self.__calculate_limit(calculated_value)

    def __calculate_limit(self, calculated_value):
        previous_limit = self.__limits[0]
        for limit in self.__limits:
            if limit > calculated_value >= previous_limit:
                return previous_limit
            else:
                previous_limit = limit
        if calculated_value < previous_limit + self.__width:
            return previous_limit
        else:
            return 'overflow'


class ValueSort(object):

    def __init__(self, bin_settings):
        # type: (List[_settings_parser.BinSettings]) -> None
        self.__bin_sorters = self.__get_bin_sorters(bin_settings)

    @staticmethod
    def __get_bin_sorters(bin_settings):
        # type: (List[_settings_parser.BinSettings]) -> List[_GetBinIndex]
        bin_searchers = []
        for bin_setting in bin_settings:
            bin_searchers.append(
                _GetBinIndex(
                    bin_setting.lower_limits_list, bin_setting.width
                )
            )
        return bin_searchers

    def sort(self, calculated_values):
        # type: (List[float]) -> List[int]
        found_locations = []
        for value, sorting in zip(calculated_values, self.__bin_sorters):
            found_locations.append(sorting.get_bin_id(value))
        return found_locations
