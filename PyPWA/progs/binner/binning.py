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

from PyPWA import AUTHOR, VERSION
from PyPWA.libs.math import vectors, particle
from PyPWA.progs.binner import _settings_parser, _multiple_writer

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class Binning(object):

    def __init__(self, settings_collection):
        # type: (_settings_parser.SettingsCollection) -> None
        self.__setting = settings_collection

    def bin(self):
        with _multiple_writer.BinManager(self.__setting) as handle:
            for event in handle:
                mass = self.__calculate_mass(event['destination'])
                handle.write(
                    {
                        'bins': self.__find_bin(mass),
                        'files': event
                    }
                )

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
