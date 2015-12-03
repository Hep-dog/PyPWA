"""
A collection of file handlers for PyPWA
"""
__author__ = "Mark Jones"
__credits__ = ["Mark Jones", "Josh Pond"]
__license__ = "MIT"
__version__ = "2.0.0"
__maintainer__ = "Mark Jones"
__email__ = "maj@jlab.org"
__status__ = "Beta0"

import data_tools
from memory import sv, kv
from abc import ABCMeta, abstractmethod
import os
import yaml


class DataInterface:
    """Interface for Data Objects"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def parse(file_location):
        pass

    @abstractmethod
    def write(file_location, data):
        pass


class Kv(DataInterface):

    @staticmethod
    def parse(file_location):
        with open(file_location) as stream:
            first_line = stream.readline()

        if "=" in first_line:
            data = kv.DictOfArrays()
        elif len(first_line.strip("\n")) == 1:
            data = kv.ListOfBooleans()
        elif len(first_line.strip("\n")) > 1:
            data = kv.ListOfFloats()
        else:
            raise TypeError("Unknown data type for {0} !".format(file_location))

        return data.parse(file_location)

    @staticmethod
    def write(file_location, data):
        data_check = data_tools.DataTypes()
        the_type = data_check.type(data)

        if the_type == "dictofarrays":
            data = kv.DictOfArrays()
        elif the_type == "listofbools":
            data = kv.ListOfBooleans()
        elif the_type == "listoffloats":
            data = kv.ListOfFloats()
        else:
            raise TypeError("Unknown type {0} !".format(the_type))

        data.write(file_location, data)


class Sv(DataInterface):

    @staticmethod
    def parse(file_location):
        file_ext = os.path.splitext(file_location)[1]

        if file_ext == ".tsv":
            parser = sv.SvParser("\t")
        elif file_ext == ".csv":
            parser = sv.SvParser(",")
        else:
            raise TypeError("Variable seperated files must end in .tsv or .csv!")

        return parser.reader(file_location)

    @staticmethod
    def write(file_location, data):
        raise NotImplementedError("Writing of Variable Seperated files is not yet supported")


class Binary(DataInterface):
    def __init__(self):
        raise NotImplementedError("There isn't any defined standard yet")


class Yaml(DataInterface):
    """YAML Parsing Object"""

    @staticmethod
    def parse(file_location):
        """Parses Yaml configuration files from disk
        Args:
            file_location (str): Path to the file
        Returns:
            dict: The values stored in a multidimensional dictionary
        """
        with open(file_location) as stream:
            saved = yaml.load(stream)
        return saved

    @staticmethod
    def write(file_location, data):
        """Writes YAML Configs to disk
        Args:
            file_location (str): Path to the file
            data (dict): Dictionary to write.
        """

        with open(file_location, "w") as stream:
            stream.write(yaml.dump(data))
