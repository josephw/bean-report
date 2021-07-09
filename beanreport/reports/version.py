"""Version-related utilities.
"""
__copyright__ = "Copyright (C) 2014-2016  Martin Blais"
__license__ = "GNU GPLv2"

import argparse

from beanreport.reports import __version__


def ArgumentParser(*args, **kwargs):
    """Add a standard --version option to an ArgumentParser.

    Args:
      *args: Arguments for the parser.
      *kwargs: Keyword arguments for the parser.
    Returns:
      An instance of ArgumentParser, with our default options set.
    """
    parser = argparse.ArgumentParser(*args, **kwargs)

    parser.add_argument('--version', '-V', action='version',
                        version=__version__)

    return parser
