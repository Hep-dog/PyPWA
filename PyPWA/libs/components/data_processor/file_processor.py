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
Main object for Parsing Data
"""

import logging
from typing import Union, Optional as Opt

import numpy

from PyPWA import Path, AUTHOR, VERSION
from PyPWA.libs.components.data_processor import (
    _plugin_finder, data_templates, exceptions
)
from PyPWA.libs.components.data_processor.cache import builder
from PyPWA.libs.math import particle

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


SUPPORTED_DATA = Union[numpy.ndarray, particle.ParticlePool]


class _DataLoader(object):

    __LOGGER = logging.getLogger(__name__ + "._DataLoader")

    def __init__(self, use_cache, clear_cache):
        # type: (bool, bool) -> None
        self.__plugin_search = _plugin_finder.PluginSearch()
        self.__cache_builder = builder.CacheBuilder(use_cache, clear_cache)

    def parse(self, file):
        # type: (Path) -> numpy.ndarray
        cache = self.__cache_builder.get_cache_interface(file)
        if cache.is_valid():
            self.__LOGGER.info("Loading cache for %s" % file)
            return cache.read_cache()
        else:
            self.__LOGGER.info("No cache found, loading file directly.")
            return self.__read_data(cache, file)

    def __read_data(self, cache, file):
        plugin = self.__load_read_plugin(file)
        data = plugin.get_plugin_memory_parser().parse(file)
        cache.write_cache(data)
        return data

    def __load_read_plugin(self, file):
        # type: (Path) -> data_templates.DataPlugin
        try:
            return self.__plugin_search.get_read_plugin(file)
        except exceptions.UnknownData:
            raise OSError


class _DataDumper(object):

    def __init__(self, use_cache, clear_cache):
        # type: (bool, bool) -> None
        self.__plugin_search = _plugin_finder.PluginSearch()
        self.__cache_builder = builder.CacheBuilder(use_cache, clear_cache)

    def write(self, file, data):
        # type: (Path, numpy.ndarray) -> None
        self.__write_data(file, data)
        cache = self.__cache_builder.get_cache_interface(file)
        cache.write_cache(data)

    def __write_data(self, file, data):
        # type: (Path, data_templates.SUPPORTED_DATA) -> None
        plugin = self.__load_write_plugin(file, data)
        found_parser = plugin.get_plugin_memory_parser()
        found_parser.write(file, data)

    def __load_write_plugin(self, file, data):
        # type: (Path, numpy.ndarray) -> data_templates.DataPlugin
        is_pool, is_basic = self.__find_data_type(data)
        try:
            return self.__plugin_search.get_write_plugin(
                file, is_pool, is_basic
            )
        except exceptions.UnknownData:
            raise RuntimeError("Can not write data!")

    @staticmethod
    def __find_data_type(data):
        types = [False, False]
        if isinstance(data, particle.ParticlePool):
            types[0] = True
        elif not data.dtype.names:
            types[1] = True
        return types


class _Iterator(object):

    def __init__(self):
        self.__plugin_fetcher = _plugin_finder.PluginSearch()

    def return_reader(self, file):
        plugin = self.__plugin_fetcher.get_read_plugin(file)
        return plugin.get_plugin_reader(file)

    def return_writer(self, file, is_particle, is_basic):
        # type: (Path, bool, bool) -> data_templates.Writer
        plugin = self.__plugin_fetcher.get_write_plugin(
            file, is_particle, is_basic
        )
        return plugin.get_plugin_writer(file)


class DataProcessor(object):

    def __init__(
            self,
            enable_cache=False,  # type: bool
            clear_cache=False,  # type: bool
    ):
        self.__loader = _DataLoader(enable_cache, clear_cache)
        self.__dumper = _DataDumper(enable_cache, clear_cache)
        self.__iterator = _Iterator()

    def parse(self, file):
        # type: (Path) -> numpy.ndarray
        return self.__loader.parse(file)

    def get_reader(self, file):
        # type: (Path) -> data_templates.Reader
        return self.__iterator.return_reader(file)

    def write(self, file, data):
        # type: (Path, data_templates.SUPPORTED_DATA) -> None
        self.__dumper.write(file, data)

    def get_writer(
            self, file, is_particle_pool=False, is_basic_type=False
    ):
        # type: (Path, Opt[bool], Opt[bool]) -> data_templates.Writer
        return self.__iterator.return_writer(
            file, is_particle_pool, is_basic_type
        )
