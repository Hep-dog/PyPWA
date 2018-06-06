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
from typing import Any, Dict, List, Optional as Opt

import tqdm

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

    def get_bin_handles_dict(
            self,
            source_file,  # type: Path
            extras,  # type: List[Path]
            root,  # type: Path
            bin_types  # type: List[_settings_parser.BinSettings]
    ):
        # type: (...) -> dict
        file_handles = dict()
        for lower_limit in self.__base_limits(bin_types):
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
    def __base_limits(bin_settings):
        lower_limits = bin_settings[0].lower_limits_list
        lower_limits.append('underflow')
        lower_limits.append('overflow')
        return lower_limits

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


class _MultipleWriter(object):

    def __init__(self, settings):
        # type: (_settings_parser.SettingsCollection) -> None
        self.__settings = settings
        self.__handle_closer = _CloseHandles()
        self.__handle_opener = _FileHandlesDict()
        self.__handles = self.__open_handles()

    def __open_handles(self):
        # type: () -> dict
        return self.__handle_opener.get_bin_handles_dict(
            self.__settings.file_settings.source_file,
            self.__settings.file_settings.extra_files,
            Path(), self.__settings.bin_settings
        )

    def close(self):
        self.__handle_closer.close_handles(self.__handles)

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


class _MultipleReader(object):

    def __init__(self, file_settings):
        # type: (_settings_parser.FileSettings) -> None
        self.__event_count = None  # type: int
        self.__processor = file_processor.DataProcessor()
        self.__source = self.__setup_source(file_settings)
        self.__extras = self.__setup_extras(file_settings)

    def __setup_source(self, file_settings):
        # type: (_settings_parser.FileSettings) -> data_templates.Reader
        main_reader = self.__processor.get_reader(file_settings.source_file)
        self.__event_count = main_reader.get_event_count()
        return main_reader

    def __setup_extras(self, file_settings):
        # type: (_settings_parser.FileSettings) -> List[data_templates.Reader]
        extras = []
        for file in file_settings.extra_files:
            reader = self.__processor.get_reader(file)
            self.__check_event_length(reader)
            extras.append(reader)
        return extras

    def __check_event_length(self, reader):
        # type: (data_templates.Reader) -> None
        if reader.get_event_count() != self.__event_count:
            raise RuntimeError("Input files have a different event count!")

    def read(self):
        # type: () -> Dict
        return {
            'destination': self.__get_source(),
            'extras': self.__get_extras()
        }

    def __get_source(self):
        return self.__source.next()

    def __get_extras(self):
        extras = []
        for extra in self.__extras:
            extras.append(extra.next())
        return extras

    def close(self):
        self.__source.close()
        for file in self.__extras:
            file.close()

    def __len__(self):
        return self.__event_count


class BinManager(object):

    def __init__(self, settings_collection, use_progress=True, position=1):
        # type: (_settings_parser.SettingsCollection, Opt[bool]) -> None
        self.__reader = _MultipleReader(settings_collection.file_settings)
        self.__writer = _MultipleWriter(settings_collection)
        self.__event_count = len(self.__reader)
        self.__progress_bar = self.__setup_progress_bar(
            use_progress, position
        )

    def __setup_progress_bar(self, use_progress, position):
        if use_progress:
            return tqdm.tqdm(
                total=self.__event_count, desc="Binning", unit_scale=True,
                unit="events", position=position
            )
        else:
            return False

    def __iter__(self):
        return self

    def __next__(self):
        return self.read()

    def next(self):
        return self.read()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __len__(self):
        return len(self.__reader)

    def read(self):
        return self.__reader.read()

    def write(self, write_packet):
        self.__increment_progress()
        self.__writer.write(write_packet)

    def __increment_progress(self):
        if self.__progress_bar:
            self.__progress_bar.update(1)

    def close(self):
        self.__reader.close()
        self.__writer.close()
        self.__progress_bar.close()
