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
Here the entry points for PyPWA are defined that use the Configuration 
package. Each function is a program.
"""

from PyPWA import AUTHOR, VERSION
from PyPWA.initializers.configurator.start import StartProgram

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION

initializer = StartProgram()


def py_fit():
    description = u"A fitting shell that allows the User " \
                  u"to select their own likelihood and function."
    configuration = {
        "description": description,
        "main": "shell fitting method",
        "main name": "General Fitting",
        "extras": None
    }
    initializer.start(configuration)


def likelihood_fit():
    description = u"Amplitude Fitting using the Likelihood Estimation " \
                  u"Method."
    configuration = {
        "description": description,
        "main": "shell fitting method",
        "main name": "Likelihood Fitting",
        "main options": {"likelihood type": "likelihood"},
        "extras": None
    }
    initializer.start(configuration)


def chi_squared_fit():
    description = u"Amplitude Fitting using the ChiSquared Method."
    configuration = {
        "description": description,
        "main": "shell fitting method",
        "main name": "Chi-Squared Fitting",
        "main options": {
            "likelihood type": "chi-squared",
            "generated length": None,
            "accepted monte carlo location": None
        },
        "extras": None
    }
    initializer.start(configuration)


def py_simulate():
    description = u"Simulation using the the Acceptance Reject Method."
    configuration = {
        "description": description,
        "main": "shell simulation",
        "main name": "Simulator",
        "main options": {
            "the type": "full",
            "max intensity": None
        },
        "extras": None
    }
    initializer.start(configuration)


def generate_intensities():
    description = u"Generates the Intensities for Rejection Method."
    configuration = {
        "description": description,
        "main": "shell simulation",
        "main name": "Intensities",
        "main options": {
            "the type": "intensities",
            "max intensity": None
        },
        "extras": None
    }
    initializer.start(configuration)


def generate_weights():
    description = u"Takes generated intensities to run through the " \
                  u"Rejection Method."
    configuration = {
        "description": description,
        "main": "shell simulation",
        "main name": "Rejection Method",
        "main options": {
            "the type": "weighting",
            "parameters": None,
            "setup name": None,
            "processing name": None,
            "function's location": None
        },
        "extras": None
    }
    initializer.start(configuration)
