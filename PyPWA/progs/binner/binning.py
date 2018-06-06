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

from PyPWA import AUTHOR, VERSION
from PyPWA.libs.math import vectors, particle
from PyPWA.progs.binner import _settings_parser, _bin_manager

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class _GetBinIndex(object):

    def __init__(self, limits):
        self.__limits = limits

    def get_bin_id(self, calculated_value):
        if calculated_value < self.__limits[0]:
            return 'underflow'
        else:
            return self.__calculate_limit(calculated_value)

    def __calculate_limit(self, calculated_value):
        previous_limit = self.__limits[0]
        for limit in self.__limits:
            if limit > calculated_value > previous_limit:
                return previous_limit
            else:
                previous_limit = limit
        return 'overflow'


class SortBins(object):

    def __init__(self, bin_settings):
        # type: (List[_settings_parser.BinSettings]) -> None
        self.__bin_sorters = self.__get_bin_sorters(bin_settings)

    @staticmethod
    def __get_bin_sorters(bin_settings):
        # type: (List[_settings_parser.BinSettings]) -> List[_GetBinIndex]
        bin_searchers = []
        for bin_setting in bin_settings:
            bin_searchers.append(_GetBinIndex(bin_setting.lower_limits_list))
        return bin_searchers

    def sort(self, calculated_values):
        # type: (List[float]) -> List[int]
        found_locations = []
        for value, sorting in zip(calculated_values, self.__bin_sorters):
            found_locations.append(sorting.get_bin_id(value))
        return found_locations


class BinType(enum.Enum):
    MASS = enum.auto()
    ENERGY = enum.auto()


class _CalculateInterface(object):

    TYPE = NotImplemented  # type: BinType

    def calculate(self, event):
        # type: (particle.ParticlePool) -> float
        raise NotImplementedError


class _CalculateMass(_CalculateInterface):

    TYPE = BinType.MASS

    def calculate(self, event):
        # type: (particle.ParticlePool) -> float
        total = self.__get_particle_total(event)
        return self.__calculate_mass(total)

    def __get_particle_total(self, event):
        # type: (particle.ParticlePool) -> vectors.FourVector
        particle_vector = self.__get_empty_four_vector()
        for event_particle in event.iterate_over_particles():
            if event_particle.id not in (1, 14):
                particle_vector += event_particle
        return particle_vector

    @staticmethod
    def __get_empty_four_vector():
        array = numpy.zeros(1, particle.NUMPY_PARTICLE_DTYPE)
        return vectors.FourVector(array)

    @staticmethod
    def __calculate_mass(total):
        # type: (vectors.FourVector) -> float
        momentum_squared = total.x**2 + total.y**2 + total.z**2
        final_value = total.y**2 - momentum_squared
        if final_value < 0:
            return -numpy.sqrt(-final_value)
        else:
            return numpy.sqrt(final_value)


class BinCalculator(object):

    def __init__(self, bin_settings):
        # type: (List[_settings_parser.BinSettings]) -> None
        self.__bins = self.__setup_bins(bin_settings)

    @staticmethod
    def __setup_bins(settings):
        bins = []
        for setting in settings:
            if setting.bin_type == BinType.MASS:
                bins.append(_CalculateMass())
            else:
                raise ValueError("Unknown bin type %s!" % setting.bin_type)
        return bins

    def calculate_bin(self, event):
        bin_values = []
        for calc_bin in self.__bins:
            bin_values.append(calc_bin.calculate(event))
        return bin_values


class Binning(object):

    def __init__(self, settings_collection):
        # type: (_settings_parser.SettingsCollection) -> None
        self.__setting = settings_collection
        self.__sorter = SortBins(settings_collection.bin_settings)
        self.__bin_calc = BinCalculator(settings_collection.bin_settings)

    def bin(self):
        with _bin_manager.BinManager(self.__setting) as handle:
            for event in handle:
                mass = self.__bin_calc.calculate_bin(event['destination'])
                handle.write(
                    {
                        'bins': self.__sorter.sort(mass),
                        'files': event
                    }
                )

