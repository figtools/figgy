from configparser import ConfigParser
from enum import Enum
from typing import Type, Union, Optional, Callable

from config import CONFIG_OVERRIDE_FILE_PATH, Config, Color
from input import Input
from utils.utils import Utils


class ConfigManager:
    """
    Offers functionality around storing/retrieving global user managed global configuration
    overrides. Operates on INI formatted configuration files.
    """

    def __init__(self, config_file: str):
        """
        :param config_file: /path/to/config_file
        """
        self.config_file = config_file
        self.config = ConfigParser()
        with open(self.config_file, 'r') as file:
            self.config.read_file(file)

    def get_or_prompt(self, config: Enum, get_it: Callable, colors_enabled=Utils.is_mac()):
        c = Color(colors_enabled)
        val = self.get_property(config)

        if val:
            print(f"\n\n{c.fg_bl}Default value found:{c.rs}")
            print(f"Key: {c.fg_gr}{config.value}{c.rs}")
            print(f"Value: {c.fg_gr}{val}{c.rs}")
            print(f"Values found in file: {c.fg_bl}{CONFIG_OVERRIDE_FILE_PATH}{c.rs}\n\n")

            selection = Input.y_n_input("Continue with this value? ", default_yes=True)
            if not selection:
                val = get_it()
        else:
            val = get_it()

        return val

    def get_property(self, key: Union[Type[Config.Section], Enum]) -> Optional[str]:
        """
        Retrieves a property from the ini formatted config file and returns its value
        :param section: [section] in the ini config to find this parameter
        :param key: The key in the provided section to look up
        :param property: name of property to retrieve
        """
        try:
            if self.config.has_option(key.__objclass__.NAME.value, key.value):
                return self.config[key.__objclass__.NAME.value][key.value]
            else:
                return None
        except Exception as e:
            print(e)

    @staticmethod
    def figgy() -> "ConfigManager":
        """
        Get an instance of the figgy user provided configuration file
        """
        return ConfigManager(CONFIG_OVERRIDE_FILE_PATH)
