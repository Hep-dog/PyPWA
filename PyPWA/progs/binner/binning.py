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
import numpy
import tqdm

from PyPWA import queue, AUTHOR, VERSION
from PyPWA.libs.components.data_processor import (
    file_processor, data_templates
)
from PyPWA.libs.math import vectors, particle
from PyPWA.progs.binner import _bin_data, _directory_manager

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class _MultipleReader(object):

    def __init__(self, file_settings):
        # type: (_bin_data.FileSettings) -> None
        self.__event_count = None  # type: int
        self.__processor = file_processor.DataProcessor()
        self.__source = self.__setup_source(file_settings)
        self.__extras = self.__setup_extras(file_settings)

    def __setup_source(self, file_settings):
        main_reader = self.__processor.get_reader(file_settings.source_file)
        self.__event_count = main_reader.get_event_count()
        return main_reader

    def __setup_extras(self, file_settings):
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

    def __len__(self):
        return self.__event_count

    def __iter__(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __next__(self):
        return self.next()

    def next(self):
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


class Binning(object):

    def __init__(self, settings_collection):
        # type: (_bin_data.SettingsCollection) -> None
        self.__setting = settings_collection

    def bin(self):
        with _MultipleReader(self.__setting.file_settings) as multiple_reader:
            self.__iterate_over_events(multiple_reader)

    def __iterate_over_events(self, multiple_reader):
        args = {
            "desc": "Binning", "unit": "events"
        }
        with _directory_manager.BinDirectoryManager(self.__setting) as write:
            for event in tqdm.tqdm(multiple_reader, **args):
                mass = self.__calculate_mass(event['destination'])
                packet = {
                    'bins': self.__find_bin(mass),
                    'files': event
                }
                write.write(packet)

    @staticmethod
    def __calculate_mass(event):
        array = numpy.zeros(1, particle.NUMPY_PARTICLE_DTYPE)
        particle_vector = vectors.FourVector(array)
        for the_particle in event.iterate_over_particles():
            if the_particle.id not in (1, 14):
                particle_vector += the_particle
        return numpy.sqrt(particle_vector.get_dot(particle_vector))*1000

    def __find_bin(self, calculated_value):
        previous_bin = None
        lower_limits = self.__setting.bin_settings[0].lower_limits_list
        for index, current_bin in enumerate(lower_limits):
            if not index:
                previous_bin = current_bin
                if current_bin > calculated_value:
                    return [600]
            if current_bin > calculated_value > previous_bin:
                return [previous_bin]
            previous_bin = current_bin
        return [current_bin]
