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

import os
from configparser import SafeConfigParser


class Settings(object):
    def __init__(self, filename):
        self.settings = SafeConfigParser()
        self.filename = filename
        self.load()

    def load(self, filename=None):
        if not filename:
            filename = self.filename

        if not os.path.exists(filename):
            print('\033[91m file is not  found : %s \033[0m' % filename)
            return False
        files = self.settings.read(filename, encoding='utf-8')

        return len(files) > 0

    def write(self):
        with open(self.filename, 'w') as configfile:
            self.settings.write(configfile)

    def get(self, section, key):
        return self.settings.get(section, key)

    def set(self, section, key, value):
        if not self.settings.has_section(section):
            self.settings.add_section(section)
        self.settings.set(section, key, value)

    def handle(self, section, name, value):
        if section not in self.settings.sections():
            print('\033[91m %s not found in sections : %s \033[0m' % (section, self.settings.sections()))
        if value:
            self.settings.set(section, name, value)
            self.write()
        else:
            return self.settings.get(section, name)
