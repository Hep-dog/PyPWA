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
Difficulty Processing for Configuration Creation
------------------------------------------------
These objects take the plugin's metadata and produces a template configuration
that can be used for output.

- _FullOptions - Renders the entire template configuration for ProcessOptions

- ProcessOptions - Takes the metadata from a plugin and the selected 
  difficulty, then parses that into a usable ruamel.yaml object that can be 
  loaded into a template configuration file.
"""

import copy
import logging

from ruamel.yaml import comments

from PyPWA import AUTHOR, VERSION
from PyPWA.core.configurator import options

__credits__ = ["Mark Jones"]
__author__ = AUTHOR
__version__ = VERSION


class _FullOptions(object):

    __logger = logging.getLogger(__name__ + ".FullOptions")
    __options = None  # type: options.Base
    __built_options = None  # type: comments.CommentedMap

    def __init__(self, options_object):
        self.__logger.addHandler(logging.NullHandler())
        self.__options = options_object
        self.__build_options()

    def __build_options(self):
        self.__set_header_into_built_options()
        self.__set_content_into_built_options()
        self.__logger.info(
            "Built the options for %s" % self.__options.plugin_name
        )

    def __set_header_into_built_options(self):
        header = comments.CommentedMap()
        header.yaml_add_eol_comment(
            self.__options.module_comment, self.__options.plugin_name
        )
        self.__built_options = header

    def __set_content_into_built_options(self):
        content = comments.CommentedMap()
        populated_content = self.__add_default_options(content)
        commented_content = self.__add_option_comments(populated_content)
        self.__built_options[self.__options.plugin_name] = commented_content

    def __add_default_options(self, content):
        for option, value in self.__options.default_options.items():
            content[option] = value
        return content

    def __add_option_comments(self, content):
        for option, comment in self.__options.option_comments.items():
            content.yaml_add_eol_comment(comment, option)
        return content

    @property
    def plugin_options(self):
        return self.__built_options

    @property
    def name(self):
        return self.__options.plugin_name

    @property
    def difficulties(self):
        return self.__options.option_difficulties.items()


class ProcessOptions(object):

    __full_options = None  # type: _FullOptions
    __processed_options = None  # type: comments.CommentedMap
    __rejection_list = None  # type: list

    def processed_options(self, options_object, requested_difficulty):
        self.__setup_options(options_object)
        self.__set_difficulty_rejection_list(requested_difficulty)
        self.__remove_difficulties()
        return self.__processed_options

    def __setup_options(self, options_object):
        self.__set_full_options(options_object)
        self.__set_processed_options()

    def __set_full_options(self, options_object):
        self.__full_options = _FullOptions(options_object)

    def __set_processed_options(self):
        self.__processed_options = self.__full_options.plugin_options
        print(repr(self.__processed_options))

    def __set_difficulty_rejection_list(self, requested_difficulty):
        if requested_difficulty == options.Levels.REQUIRED:
            self.__rejection_list = [
                options.Levels.OPTIONAL,
                options.Levels.ADVANCED
            ]
        elif requested_difficulty == options.Levels.OPTIONAL:
            self.__rejection_list = [options.Levels.ADVANCED]
        elif requested_difficulty == options.Levels.ADVANCED:
            self.__rejection_list = []
        else:
            raise ValueError(
                "Unknown difficulty: %s" % repr(requested_difficulty)
            )

    def __remove_difficulties(self):
        for option, difficulty in self.__full_options.difficulties:
            if difficulty in self.__rejection_list:
                self.__processed_options[self.__full_options.name].pop(option)
