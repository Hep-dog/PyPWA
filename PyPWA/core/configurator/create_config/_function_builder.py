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
Writer for Example Functions
----------------------------

- _GetFunctionLocation - Takes the configuration file location then derives
  a function file location using the same name.
  
- _FunctionStorage - a simple object used for passing around data about the 
  imports and functions.
  
- _BuildStorage - Takes the plugin list and uses it to populate the 
  _FunctionStorage object.

- _FileBuilder - takes all the storage object and uses it to build the actual
  text file that is to be written to disk.
  
- _FileWriter - A simple object that takes the file and function location and
  writes the rendered functions to disk.
  
- FunctionHandler - The main object to interact with to generate a functions
  file.
"""

import os

from PyPWA import AUTHOR, VERSION

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class _GetFunctionLocation(object):

    __function_location = None

    def process_location(self, configuration_location):
        self.__function_location = ""
        file_name = os.path.splitext(configuration_location)[0]
        self.__function_location += file_name + ".py"

    @property
    def function_location(self):
        return self.__function_location


class _FunctionStorage(object):

    imports = None
    functions = None

    def __init__(self):
        self.imports = set()
        self.functions = []


class _BuildStorage(object):

    __plugin_list = None
    __storage = None

    def __init__(self):
        self.__storage = _FunctionStorage()

    def process_plugin_list(self, plugin_list):
        self.__plugin_list = plugin_list
        self.__process_main()
        self.__process_plugins()

    def __process_main(self):
        if self.__plugin_list.shell.defined_function:
            self.__process_function(self.__plugin_list.shell)

    def __process_plugins(self):
        for plugin in self.__plugin_list.plugins:
            if plugin.defined_function:
                self.__process_function(plugin)

    def __process_function(self, plugin):
        self.__add_imports(plugin.defined_function.imports)
        self.__add_function(plugin.defined_function.functions)

    def __add_imports(self, imports):
        for the_import in imports:
            self.__storage.imports.add(the_import)

    def __add_function(self, functions):
        for the_function in functions:
            self.__storage.functions.append(the_function)

    @property
    def storage(self):
        return self.__storage


class _FileBuilder(object):

    __imports = None
    __functions = None
    __file = None

    def build(self, storage):
        self.__file = ""
        self.__process_imports(storage)
        self.__process_functions(storage)
        self.__render_imports()
        self.__render_functions()

    def __process_imports(self, storage):
        self.__imports = sorted(storage.imports)

    def __process_functions(self, storage):
        self.__functions = sorted(storage.functions)

    def __render_imports(self):
        for the_import in self.__imports:
            self.__file += "import %s\n" % the_import

    def __render_functions(self):
        for the_function in self.__functions:
            self.__file += "\n" + the_function
        self.__file += "\n"

    @property
    def functions_file(self):
        return self.__file


class _FileWriter(object):

    @staticmethod
    def write_file(file_location, file_data):
        with open(file_location, "w") as stream:
            stream.write(file_data)


class FunctionHandler(object):

    __file_location = _GetFunctionLocation()
    __builder = _FileBuilder()
    __writer = _FileWriter()
    __storage = None

    def __init__(self):
        self.__storage = _BuildStorage()

    def output_functions(self, plugin_list, configuration_location):
        self.__file_location.process_location(configuration_location)
        self.__storage.process_plugin_list(plugin_list)
        self.__builder.build(self.__storage.storage)
        self.__writer.write_file(
            self.__file_location.function_location,
            self.__builder.functions_file
        )