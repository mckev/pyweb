import configparser


class Config:
    """ Read configuration file """

    def __init__(self, filename):
        self._config = configparser.ConfigParser()
        self._config.read(filename)

    def get(self, key, section='general'):
        # Notes on https://docs.python.org/3/library/configparser.html
        #    - Section names are case sensitive but keys are not
        #    - Leading and trailing white-space is removed from keys and values
        #    - It always store values as strings
        if section not in self._config:
            return None
        elif key not in self._config[section]:
            return None
        else:
            return self._config[section][key]
