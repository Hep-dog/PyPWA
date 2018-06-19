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

import multiprocessing
import time
from typing import List

from PyPWA import queue, AUTHOR, VERSION
from PyPWA.progs.binner import (
    _settings_parser, _bin_manager, _calculate_bins, _folder_finder
)

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class _BinProcess(multiprocessing.Process):

    def __init__(
            self,
            settings_collection,  # type: _settings_parser.SettingsCollection
            error_queue,  # type: multiprocessing.Queue
            position,  # type: int
    ):
        # type: (...) -> None
        super(_BinProcess, self).__init__()
        self.daemon = True
        self.__error_queue = error_queue
        self.__count = position
        self.__setting = settings_collection
        self.__sorter = _folder_finder.ValueSort(
            settings_collection.bin_settings
        )
        self.__bin_calc = _calculate_bins.BinCalculator(
            settings_collection.bin_settings
        )

    def run(self):
        try:
            self.__bin()
        except Exception as error:
            self.__error_queue.put(True)
            raise error

    def __bin(self):
        with _bin_manager.BinManager(
                self.__setting, True, self.__count
        ) as handle:
            for event in handle:
                mass = self.__bin_calc.calculate_bin(event['destination'])
                handle.write(
                    {
                        'bins': self.__sorter.sort(mass),
                        'files': event
                    }
                )


class Binning(object):

    def __init__(self):
        # type: (List[_settings_parser.SettingsCollection]) -> None
        self.__error_queue = multiprocessing.Queue()
        self.__processes = None  # type: List[_BinProcess]

    def bin_collections(self, collections):
        self.__setup_processes(collections)
        self.__start_processes()
        self.__wait_for_binning_to_finish()

    def __setup_processes(self, settings_collections):
        processes = []
        for index, settings in enumerate(settings_collections):
            processes.append(_BinProcess(settings, self.__error_queue, index))
        self.__processes = processes

    def __start_processes(self):
        for process in self.__processes:
            process.start()

    def __wait_for_binning_to_finish(self):
        running = True
        while running:
            self.__check_queues_for_errors()
            running = self.__processes_are_alive()
            time.sleep(1.5)

    def __check_queues_for_errors(self):
        try:
            error = self.__error_queue.get_nowait()
        except queue.Empty:
            error = False
        finally:
            if error:
                self.__terminate_processes()

    def __terminate_processes(self):
        for process in self.__processes:
            process.terminate()

    def __processes_are_alive(self):
        for process in self.__processes:
            if process.is_alive():
                return True
        return False


