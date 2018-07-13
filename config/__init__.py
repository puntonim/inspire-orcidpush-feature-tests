import os

import ConfigParser


config = ConfigParser.SafeConfigParser()
config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
config.read(config_file)


def get(section, name):
    try:
        return config.get(section, name)
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        return None
