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

from PyPWA import AUTHOR, VERSION
from PyPWA.initializers.configurator import options
from PyPWA.libs import configuration_db
from PyPWA.libs.components import data_processor
from PyPWA.progs.binner import _settings_parser, binning

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class _ConfiguredBinning(object):

    def __init__(self):
        self.__settings = _settings_parser.SettingsFactory()
        self.__binning = binning.Binning()
        self.__db = configuration_db.Connector()

    def start(self):
        settings = self.__db.read("multiple binning")
        collections = self.__settings.get_collections(settings)
        self.__binning.bin_collections(collections)


class MultipleBinning(options.Program):

    def __init__(self):
        self.name = "multiple binning"
        self.module_comment = "PyBinning, A python data binning utility."

    def get_required_components(self):
        return [data_processor.DataConf()]

    def get_start(self):
        return _ConfiguredBinning()

    def get_default_options(self):
        return {
            'files':
                [
                    {
                        'source': "raw_events.gamp",
                        'extras': [
                            'passfail.pf',
                            'qfactor.qf'
                        ]
                    }
                ],
            'bin settings':
                [
                    {
                        'binning type': 'mass',
                        'lower limit': 100,
                        'upper limit': 1000,
                        'width of each bin': 100
                    }
                ]
        }

    def get_option_difficulties(self):
        return None

    def get_option_types(self):
        return None

    def get_option_comments(self):
        return None
