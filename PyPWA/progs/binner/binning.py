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
from typing import List
import numpy

from PyPWA import Path, AUTHOR, VERSION

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class BinErrors(enum.Enum):
    Error = enum.auto


class DataSort(object):

    def __init__(self, directory, postfix, bin_edges, bin_count):
        # type: (Path, List[int, int], int) -> None
        self.__bins = self.__calculate_bins(sorted(bin_edges), bin_count)
        self.__tracker = self.__prime_tracker(directory, postfix, self.__bins)

    @staticmethod
    def __calculate_bins(bin_edges, bin_count):
        # type: (List[int, int], int) -> List[int]
        bin_range = numpy.ptp(bin_edges)
        bin_size = int(bin_range / bin_count)
        stop = int(bin_range[0]+bin_size*bin_count)
        return list(range(bin_range[0], stop, bin_size))

    @staticmethod
    def __prime_tracker(directory, postfix, bins):
        tracker = dict()
        for the_bin in bins:
            tracker[the_bin] = {
                'directory': directory / str(the_bin) + postfix,
                'writer': False
            }
        return tracker

    def initialize(self):
        self.__create_directories()
        self.__open_file_handles()

    def __create_directories(self):
        for bin_info in self.__tracker.items():
            bin_info[1]['directory'].mkdir(parents=True, exist_ok=True)

    def __open_file_handles(self):
        pass # For now...

    def write_bin(self, bin_value, event):
        bin_location = self.__get_bin_location(bin_value)
        if bin_location == BinErrors.Error:
            print("Skipping due to error!")
            return

        self.__tracker[bin_location]['writer'].write(event)

    def __get_bin_location(self, bin_value):
        previous_bin = None
        for index, current_bin in enumerate(self.__bins):
            if not index:
                previous_bin = current_bin
                if current_bin > bin_value:
                    print("Underflow!")
                    return BinErrors.Error

            if current_bin > bin_value > previous_bin:
                return previous_bin

        print("Overflow!")
        return BinErrors.Error

    def close(self):
        for bin_info in self.__tracker.items():
            bin_info[1]['writer'].close()

