import os

import ConfigParser


_config = ConfigParser.SafeConfigParser()
_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
_config.read(_config_file)


def get(section, name):
    try:
        return _config.get(section, name)
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        return None


ENV = None
