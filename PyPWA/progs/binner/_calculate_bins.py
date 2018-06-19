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

from PyPWA import AUTHOR, VERSION
from PyPWA.libs.math import particle, reaction
from PyPWA.progs.binner import _settings_parser

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class BinType(enum.Enum):
    MASS = enum.auto()
    T = enum.auto()
    T_PRIME = enum.auto()


class _CalculateInterface(object):

    TYPE = NotImplemented  # type: BinType

    def calculate(self, event):
        # type: (particle.ParticlePool) -> float
        raise NotImplementedError


class _CalculateMass(_CalculateInterface):

    TYPE = BinType.MASS

    def calculate(self, event):
        # type: (particle.ParticlePool) -> float
        return reaction.m_result(event) * 1000


class _CalculateT(_CalculateInterface):

    def calculate(self, event):
        # type: (particle.ParticlePool) -> float
        return reaction.t(event) * 1000


class _CalculateTPrime(_CalculateInterface):

    def calculate(self, event):
        # type: (particle.ParticlePool) -> float
        return reaction.t_prime(event) * 1000


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
            elif setting.bin_type == BinType.T:
                bins.append(_CalculateT())
            elif setting.bin_type == BinType.T_PRIME:
                bins.append(_CalculateTPrime())
            else:
                raise ValueError("Unknown bin type %s!" % setting.bin_type)
        return bins

    def calculate_bin(self, event):
        bin_values = []
        for calc_bin in self.__bins:
            bin_values.append(calc_bin.calculate(event))
        return bin_values
