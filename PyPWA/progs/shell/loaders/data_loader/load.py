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
Data Loading, the main place to load data for the Shell
-------------------------------------------------------
Loads all the data from setup_dataset and filters it with _bin_filter,
then exposes that through it's properties.
"""

import logging
from typing import Dict, Union
from typing import Optional as Opt

import numpy

from PyPWA import AUTHOR, VERSION
from PyPWA.libs.interfaces import data_loaders
from PyPWA.progs.shell.loaders.data_loader import _bin_filter
from PyPWA.progs.shell.loaders.data_loader import _setup_dataset
from PyPWA.progs.shell.loaders.data_loader import _dataset_storage

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class DataLoading(object):

    __LOGGER = logging.getLogger(__name__ + ".DataLoading")

    def __init__(
            self,
            parser,  # type: data_loaders.ParserPlugin
            data,  # type: str
            internal_data=None,  # type: Opt[Dict[str, str]]
            qfactor=None,  # type: Opt[str]
            monte_carlo=None  # type: Opt[str]
    ):
        # type: (...) -> None
        if not internal_data:
            internal_data = {}

        self.__storage = None  # type: _dataset_storage.DataStorage

        self.__loader = _setup_dataset.LoadData(
            parser, data, internal_data, qfactor, monte_carlo
        )
        self.__filter = _bin_filter.BinFilter()
        self.__load_data()

    def __load_data(self):
        storage = self.__loader.load()
        self.__storage = self.__filter(storage)

    def write(self, file_location, data):
        # type: (str, numpy.ndarray) -> None
        self.__loader.write(file_location, data)

    @property
    def data(self):
        # type: () -> numpy.ndarray
        return self.__storage.data

    @property
    def qfactor(self):
        # type: () -> numpy.ndarray
        return self.__storage.qfactor

    @property
    def monte_carlo(self):
        # type: () -> Union[numpy.ndarray, None]
        return self.__storage.monte_carlo

    @property
    def binned(self):
        # type: () -> numpy.ndarray
        return self.__storage.binned

    @property
    def event_errors(self):
        # type: () -> numpy.ndarray
        return self.__storage.event_errors

    @property
    def expected_values(self):
        # type: () -> numpy.ndarray
        return self.__storage.expected_values

    @property
    def single_array(self):
        # type: () -> numpy.ndarray
        return self.__storage.single_array
