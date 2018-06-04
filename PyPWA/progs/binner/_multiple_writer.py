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
from typing import Any, Dict, List

from PyPWA import Path, AUTHOR, VERSION
from PyPWA.libs.components.data_processor import (
    file_processor, data_templates
)
from PyPWA.progs.binner import _settings_parser

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class _OpenFileHandles(object):

    def __init__(self):
        # type: () -> None
        self.__parser = file_processor.DataProcessor()

    def get_file_handles(self, source, extras, destination):
        # type: (Path, List[Path], Path) -> Dict[str, Any]
        self.__create_file_tree(destination)
        return {
            'destination': self.__process_single_file(source, destination),
            'extras': self.__process_multiple_files(extras, destination)
        }

    @staticmethod
    def __create_file_tree(destination):
        # type: (Path) -> None
        destination.mkdir(parents=True, exist_ok=True)

    def __process_single_file(self, file, destination):
        # type: (Path, Path) -> data_templates.Writer
        return self.__parser.get_writer(
            destination / file.name, is_particle_pool=True
        )

    def __process_multiple_files(self, files, destination):
        # type: (List[Path], Path) -> List[data_templates.Writer]
        handler_list = []
        for file in files:
            handler_list.append(self.__process_single_file(file, destination))
        return handler_list


class _FileHandlesDict(object):

    def __init__(self):
        self.__get_file_handles = _OpenFileHandles()

    def get_bin_handles_dict(self, source_file, extras, root, bin_types):
        # type: (Path, List[Path], Path, List[_settings_parser.BinSettings]) -> dict
        file_handles = dict()
        for lower_limit in bin_types[0].lower_limits_list:
            destination = self.__get_destination(root, lower_limit, bin_types)
            if len(bin_types[1:]):
                file_handles[lower_limit] = self.get_bin_handles_dict(
                    source_file, extras, destination, bin_types[1:]
                )
            else:
                file_handles[lower_limit] = self.__produce_file_handles(
                    source_file, extras, destination
                )
        return file_handles

    @staticmethod
    def __get_destination(root, lower_limit, bin_types):
        # type: (Path, int, List[_settings_parser.BinSettings]) -> Path
        prefix = bin_types[0].get_calculation_prefix()
        destination = root / (str(lower_limit) + prefix)
        return destination

    def __produce_file_handles(self, source, extras, destination):
        # type: (Path, List[Path], Path) -> Dict
        return self.__get_file_handles.get_file_handles(
            source, extras, destination
        )


class _CloseHandles(object):

    def close_handles(self, directory_dictionary):
        # type: (dict) -> None
        for value in directory_dictionary.values():
            if 'destination' in value:
                self.__close_handles(value)
            else:
                self.close_handles(value)

    @staticmethod
    def __close_handles(value):
        # type: (Dict) -> None
        value['destination'].close()
        for extra in value['extras']:
            extra.close()


class BinWriter(object):

    def __init__(self, settings):
        # type: (_settings_parser.SettingsCollection) -> None
        self.__handles = None
        self.__opened = False
        self.__settings = settings
        self.__handle_closer = _CloseHandles()
        self.__handle_opener = _FileHandlesDict()

    def open(self):
        if not self.__opened:
            self.__handles = self.__handle_opener.get_bin_handles(
                self.__settings.file_settings.source_file,
                self.__settings.file_settings.extra_files,
                Path(), self.__settings.bin_settings
            )
            self.__opened = True
        else:
            raise RuntimeError("Directory Manager is already open!")

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.__opened:
            self.__handle_closer.close_handles(self.__handles)
            self.__opened = False
        else:
            raise RuntimeError("Directory Manager isn't open!")

    def write(self, write_packet):
        # type: (Dict) -> None
        writers = self.__get__writers(write_packet['bins'])
        self.__write_packet(writers, write_packet['files'])

    def __get__writers(self, bins):
        # type: (List[int]) -> Dict
        sample = self.__handles
        for index_bin in bins:
            sample = sample[index_bin]
        return sample

    @staticmethod
    def __write_packet(writers, files):
        # type: (dict, dict) -> None
        writers['destination'].write(files['destination'])
        for packet in zip(writers['extras'], files['extras']):
            packet[0].write(packet[1])
