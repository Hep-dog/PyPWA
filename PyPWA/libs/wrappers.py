"""
Entry point for console GeneralShell
"""
__author__ = "Mark Jones"
__credits__ = ["Mark Jones"]
__license__ = "MIT"
__version__ = "2.0.0"
__maintainer__ = "Mark Jones"
__email__ = "maj@jlab.org"
__status__ = "Beta0"

import os


def start_builder(fn):
    def builder():
        name = fn.__name__
        cwd = os.getcwd()
        args = fn()
    return builder()