"""
This class is used to load configuration files.

These files should be formatted with sections and variables.

Example file (between the dashed lines):
--------------------------------------------
[SectionName1]
variable1 = abcdef
variable2 = ghijkl

[SectionName2]
variable1 = zyxwvu
variable2 = tsrqpo
--------------------------------------------

The subclasses should set the filename variable and the call the load() method.

This class provides the Get and Set method, but all subclasses should implement
their specific getters and setters and prevent other direct access to values.
This way the exact section name and variable name only have to be declared once.
"""

# Total imports
import os
# Partial imports
from configparser import ConfigParser
from appdirs import *
# Local imports
# from plebnet.utilities import logger


class Settings(object):
	def __init__(self, filename):
		self.settings = ConfigParser()
		self.filename = filename

	def load(self, filename=None):
		if not filename:
			filename = self.filename

		if not os.path.exists(filename):
			return False
		files = self.settings.read(filename, encoding='utf-8')
		return len(files) > 0

	def get(self, section, key):
		return self.settings.get(section, key)

	def set(self, section, key, value):
		if not self.settings.has_section(section):
			self.settings.add_section(section)
		self.settings.set(section, key, value)
