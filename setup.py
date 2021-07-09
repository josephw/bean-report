#!/usr/bin/env python3
"""
Install script for beanreport.
"""
__copyright__ = "Copyright (C) 2008-2011, 2013-2016  Martin Blais"
__license__ = "GNU GPLv2"


import re
import subprocess

from setuptools import setup, find_packages, Extension

# Read the version.
with open("beanreport/VERSION") as version_file:
    version = version_file.read().strip()
assert isinstance(version, str)

# Create a setup.
# Please read: http://furius.ca/beancount/doc/install about version numbers.
setup(name="bean-report",
      version=version,
      description="A legacy reporting tool for Beancount.",
      long_description=
      """
      A legacy reporting tool for Beancount.

      bean-report has been removed from Beancount v3. This a fork of a subset
      of the supported reports. Unless you specifically need these reports,
      you should prefer Fava or bean-query.
      """,

      license="GNU GPLv2 only",
      author="Martin Blais",
      author_email="blais@furius.ca",
      url="https://github.com/josephw/bean-report",
      download_url="https://github.com/josephw/bean-report",
      packages=find_packages(),

      package_data = {
          'beanreport': ['VERSION'],
          'beanreport.reports': ['*.html'],
      },

      install_requires = [
          'pyparsing<3,>=2.4.2',
          'beancount>=2.3,<3',

          # Testing support now uses the pytest module.
          'pytest',
      ],

      entry_points = {
          'console_scripts': [
              'bean-report = beanreport.reports.report:main',
              'bean-report.new = beanreport.reports.report:main',
          ]
      },

      python_requires='>=3.5',
)
