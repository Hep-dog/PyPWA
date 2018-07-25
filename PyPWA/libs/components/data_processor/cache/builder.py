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
Memory Caching
--------------
The objects in this file are dedicated to saving and writing chunks of
memory to file for quick loading when the data is loaded into memory
again.

- _CacheInterface - A simple interface object to _WriteCache and _ReadCache

- CacheBuilder - Builds the _CacheInterface using the other cache types
  depending on the supplied booleans.
"""

import logging
from typing import Any

from PyPWA import Path, AUTHOR, VERSION
from PyPWA.libs.components.data_processor.cache import (
    _basic_info, _clear_cache, _no_cache, _standard_cache, _template,
)

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class _CacheInterface(object):

    def __init__(self, read_cache, write_cache):
        # type: (_template.ReadInterface, _template.WriteInterface) -> None
        self.__read_cache = read_cache
        self.__write_cache = write_cache

    def write_cache(self, data):
        # type: (Any) -> None
        self.__write_cache.write_cache(data)

    def is_valid(self):
        return self.__read_cache.is_valid()

    def read_cache(self):
        """
        :raises cache.CacheError: If the hash has changed, or is corrupt.
        """
        return self.__read_cache.get_cache()


class CacheBuilder(object):

    __LOGGER = logging.getLogger(__name__ + ".CacheBuilder")

    def __init__(self, use_cache, clear_cache):
        # type: (bool, bool) -> None
        self.__use_cache = use_cache
        self.__clear_cache = clear_cache

    def get_cache_interface(self, file_location):
        # type: (Path) -> _CacheInterface
        info_object = self.__get_info_object(file_location)
        reader = self.__get_reader(info_object)
        writer = self.__get_writer(info_object)
        return _CacheInterface(reader, writer)

    @staticmethod
    def __get_info_object(file_location):
        # type: (Path) -> _basic_info.FindBasicInfo
        info = _basic_info.FindBasicInfo()
        info.setup_basic_info(file_location)
        return info

    def __get_reader(self, info):
        # type: (_basic_info.FindBasicInfo) -> _template.ReadInterface
        if not self.__use_cache or not info.file_hash:
            self.__LOGGER.debug("No Read Cache selected.")
            return _no_cache.NoRead()
        elif self.__clear_cache:
            self.__LOGGER.debug("Clear Cache selected.")
            return _clear_cache.ClearCache(info)
        else:
            self.__LOGGER.debug("Read Cache selected.")
            return _standard_cache.ReadCache(info)

    def __get_writer(self, info):
        # type: (_basic_info.FindBasicInfo) -> _template.WriteInterface
        if not self.__use_cache:
            self.__LOGGER.debug("No Write Cache selected.")
            return _no_cache.NoWrite()
        else:
            self.__LOGGER.debug("Write Cache selected.")
            return _standard_cache.WriteCache(info)
