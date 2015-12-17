import configparser
import os

from xdg import BaseDirectory


class IndicatorConfig:

    types = {
        'monitor': str,
        'enabled': bool
    }

    defaults = {
        'enabled': 'False',
        'monitor': ''
    }

    def __init__(self):

        config_dir = BaseDirectory.save_config_path('networktablet-indicator')
        self.config_file = os.path.join(config_dir, 'config.ini')
        print(self.config_file)

        self.configParser = configparser.ConfigParser(
            defaults=self.defaults,
            default_section='Networktablet'
        )

        self.typeMapping = {
            bool: (
                lambda key: self.configParser.getboolean(self.configParser.default_section, key),
                lambda key, value: self.configParser[self.configParser.default_section].__setitem__(key, str(value))
            ),
            str: (
                lambda key: self.configParser.get(self.configParser.default_section, key),
                lambda key, value: self.configParser[self.configParser.default_section].__setitem__(key, value)
            )
        }

        self.configParser.read(self.config_file)

    def __getitem__(self, key):
        if key in self.types:
            return self.typeMapping[self.types[key]][0](key)
        return self.configParser[key]

    def __setitem__(self, key, value):
        if key in self.types:
            self.typeMapping[self.types[key]][1](key, value)
        else:
            self.configParser[self.configParser.default_section][key] = value
        self.save()

    def save(self):
        with open(self.config_file, 'w') as config_file:
            self.configParser.write(config_file)
