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
import tqdm
import multiprocessing
from typing import Any, Dict, List, Optional as Opt

from PyPWA import Path, AUTHOR, VERSION
from PyPWA.libs.components.data_processor import (
    file_processor, data_templates
)
from PyPWA.progs.binner import _bin_data

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class _DictTemplate(object):

    def __init__(self, source, extras, destination):
        # type: (Path, List[Path], Path) -> None
        self.__parser = file_processor.DataProcessor()
        self.__source = source
        self.__extras = extras
        self.__destination = destination
        self.__dictionary = {
            "destination": data_templates.Writer(),
            'extras': []
        }
        self.__setup_dict()

    def __setup_dict(self):
        self.__destination.mkdir(parents=True, exist_ok=True)
        self.__dictionary['destination'] = self.__process_single_file(
            self.__source
        )
        self.__dictionary['extras'] = self.__process_multiple_files(
            self.__extras
        )

    def __process_single_file(self, file):
        return self.__parser.get_writer(
            self.__destination / file.name, is_particle_pool=True
        )

    def __process_multiple_files(self, files):
        handler_list = []
        for file in files:
            handler_list.append(self.__process_single_file(file))
        return handler_list

    @property
    def produced_dict(self):
        return self.__dictionary


class _FileHandles(object):

    def __init__(
            self,
            source_file,  # type: Path
            extras,  # type: List[Path]
            root,  # type: Path
            bin_types,   # type: List[_bin_data.BinSettings]
    ):
        # type: (...) -> None
        self.__source_file = source_file
        self.__extras = extras
        self.__root = root
        self.__bin_type = bin_types
        self.__current_bin = bin_types[0]
        self.__child_bins = bin_types[1:]
        self.__file_handles = dict()
        self.__iterate_over_bins()

    def __iterate_over_bins(self):
        prefix = self.__current_bin.get_calculation_prefix()
        for lower_limit in self.__current_bin.lower_limits_list:
            destination = self.__root / (str(lower_limit) + prefix)
            if len(self.__child_bins):
                child = self.__append_child(destination)
                self.__file_handles[lower_limit] = child
            else:
                file_handles = self.__produce_file_handles(destination)
                self.__file_handles[lower_limit] = file_handles

    def __append_child(self, destination):
        child = _FileHandles(
            self.__source_file, self.__extras, destination,self.__child_bins
        )
        return child.file_handles

    def __produce_file_handles(self, destination):
        file_handles = _DictTemplate(
            self.__source_file, self.__extras, destination
        )
        return file_handles.produced_dict

    @property
    def file_handles(self):

        return self.__file_handles


class ConsumerProcess(multiprocessing.Process):

    def __init__(
            self,
            receive_queue,  # type: multiprocessing.Queue
            source_file,  # type: Path
            extras,  # type: List[Path]
            root,  # type: Path
            event_count,  # type: int
            bin_type  # type: List[_bin_data.BinSettings]
    ):
        # type: (...) -> None
        super(ConsumerProcess, self).__init__()
        self.daemon = True
        self.__file_handles = None

        self.__source_file = source_file
        self.__extras = extras
        self.__root = root
        self.__bin_type = bin_type
        self.__receive_queue = receive_queue
        self.__event_count = event_count

    def run(self):
        self.__file_handles = self.__get_file_handles()
        for event in tqdm.trange(
                self.__event_count, desc="Sorting and Writing",
                unit="events", position=1
        ):
            self.__process_event()
        self.__close_handles()

    def __get_file_handles(self):
        handles = _FileHandles(
            self.__source_file, self.__extras,
            self.__root, self.__bin_type
        )
        return handles.file_handles

    def __process_event(self):
        event = self.__receive_queue.get(True)
        bin_writers = self.__get_writer(event['bins'])
        self.__write_source_file(bin_writers, event)
        self.__write_extras(bin_writers, event)

    def __get_writer(self, bins, dictionary=False):
        if not dictionary:
            dictionary = self.__file_handles

        if isinstance(bins, list) and len(bins) > 1:
            return self.__get_writer(bins[1:], dictionary[bins[0]])
        else:
            return dictionary[bins[0]]

    @staticmethod
    def __write_source_file(bin_writers, received):
        bin_writers['destination'].write(received['files']['destination'])

    @staticmethod
    def __write_extras(bin_writers, received):
        packets = zip(bin_writers['extras'], received['files']['extras'])
        for write_packet in packets:
            write_packet[0].write(write_packet[1])

    def __close_handles(self, dictionary=False):
        # type: (Opt[Dict[str, Any]]) -> None
        if not dictionary:
            dictionary = self.__file_handles

        for item in dictionary.items():
            if 'destination' in item[1]:
                item[1]['destination'].close()
                for file in item[1]['extras']:
                    file.close()
            else:
                self.__close_handles(dictionary)