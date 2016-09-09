#    PyPWA, a scientific analysis toolkit.
#    Copyright (C) 2016  JLab
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyPWA import VERSION, LICENSE, STATUS
from PyPWA.core_libs import templates

__author__ = ["Mark Jones"]
__credits__ = ["Mark Jones"]
__maintainer__ = ["Mark Jones"]
__email__ = "maj@jlab.org"
__status__ = STATUS
__license__ = LICENSE
__version__ = VERSION


class MultiNest(templates.MinimizerTemplate):
    """
    This will be elegant and amazing, eventually.
    """

    builtin_function = u"""\
The function with all the documentation required to build the parameter
space. Right now we don't understand this.
"""


class MultiNestOptions(templates.OptionsTemplate):

    def _plugin_name(self):
        return "MultiNest"

    def _plugin_interface(self):
        return MultiNest

    def _plugin_type(self):
        return self._minimization

    def _plugin_arguments(self):
        return False

    def _plugin_requires(self):
        return self._build_function("numpy", "def function")

    def _default_options(self):
        return False

    def _option_levels(self):
        return False

    def _option_types(self):
        return False

    def _main_comment(self):
        return False

    def _option_comments(self):
        return False
