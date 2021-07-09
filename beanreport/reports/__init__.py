"""Routines to produce various reports, either to HTML or to text.
"""
__copyright__ = "Copyright (C) 2014, 2016  Martin Blais"
__license__ = "GNU GPLv2"

# Read in the VERSION number from package data.
from os import path
with open(path.join(path.dirname(__file__), "..", "VERSION")) as version_file:
    __version__ = version_file.read().strip()
