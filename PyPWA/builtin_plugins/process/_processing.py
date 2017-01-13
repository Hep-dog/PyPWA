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
The processes and their factories are defined here. The current supported
methods are Duplex for worker processes and Simplex for offload processes.
"""


from PyPWA import AUTHOR, VERSION
from PyPWA.builtin_plugins.process.communication import factory
from PyPWA.builtin_plugins.process import _processes

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class CalculationFactory(object):

    @staticmethod
    def simplex_build(process_kernels):

        count = len(process_kernels)
        processes = []

        sends, receives = factory.CommunicationFactory.simplex_build(count)

        for index, internals in enumerate(zip(process_kernels, sends)):
            processes.append(
                _processes.SimplexProcess(index, internals[0], internals[1])
            )

        return [processes, receives]

    @staticmethod
    def duplex_build(process_kernels):
        count = len(process_kernels)
        processes = []
        main_com, process_com = factory.CommunicationFactory.duplex_build(count)

        for index, internals in enumerate(zip(process_kernels, process_com)):
            processes.append(_processes.DuplexProcess(
                index, internals[0], internals[1]
            ))
            processes.append(
                _processes.DuplexProcess(index, internals[0], internals[1])
            )

        return [processes, main_com]
