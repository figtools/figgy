from configparser import ConfigParser
from enum import Enum
from typing import Type, Union, Optional, Callable, Any

from figcli.config import CONFIG_OVERRIDE_FILE_PATH, Config, EMPTY_CONFIG
from figcli.config.style.terminal_factory import TerminalFactory
from figcli.input import Input
from figcli.utils.utils import Utils
from threading import Lock
from os import path


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
        self.config = None
        self._lock = Lock()
        self._load()

    def _load(self):
        self.config = ConfigParser()
        with open(self.config_file, 'r') as file:
            self.config.read_file(file)

    def set(self, key: Union[Type[Config.Section], Enum], val: Any) -> None:
        """
        Set the value in self.config_file for key: KEY
        Values are forced to strings if non-string values are passed
        :param key: Key to set in the file.
        :param val: Value to set.
        """
        # Update in case file changed on FS.
        with self._lock:
            self._load()

        if isinstance(val, bool):
            val = str(val).lower()
        else:
            val = str(val)

        self.config.set(key.__objclass__.NAME.value, key.value, val)

        with open(self.config_file, "w") as file:
            self.config.write(file)

    def get_or_prompt(self, key: Enum, get_it: Callable, colors_enabled=Utils.is_mac(), force_prompt=False,
                      desc: str = None) -> str:
        """
        Retrieves a value from the config_file based on the provided ENUM's value.
        If the value is unset, executes the get_it() method provided to retrieve the value, then returns it.

        If the user selects something _other_ than the default, overwrite the original value in the config file
        :param key: Enum representing the config value to fetch
        :param get_it: Method to execute if `config` is not in the configured config_file
        :param colors_enabled: Whether or not to enable colored output for the prompt if a config is found in config_file
        :param optional description to provide context when user is prompted.
        :return: String value from the config file, or the result of get_it()
        """
        c = TerminalFactory(colors_enabled).instance().get_colors()
        val = self.get_property(key)
        selection = None

        if val or force_prompt:
            if not force_prompt:
                print(f"\n\n{c.fg_bl}Default value found:{c.rs}")
                print(f"Key: {c.fg_gr}{key.value}{c.rs}")
                print(f"Value: {c.fg_gr}{val}{c.rs}")
                if desc:
                    print(f"Description: {desc}")

                selection = Input.y_n_input(f"Continue with `{val}`? ", default_yes=True)

            if not selection or force_prompt:
                original_val = val
                val = get_it()
                if val != original_val:
                    print(f"\n\nYou selected to overwrite the default. Updating default value:"
                          f"\nKey: {c.fg_gr}{key.value}{c.rs}"
                          f"\nFrom: {c.fg_yl}{original_val}{c.rs}"
                          f"\nTo: {c.fg_gr}{val}{c.rs}"
                          f"\nIn file {c.fg_bl}{self.config_file}{c.rs}")

                    self.set(key, val)

        else:
            val = get_it()

        return val

    def get_property(self, key: Union[Type[Config.Section], Enum], default=None) -> Optional[str]:
        """
        Retrieves a property from the ini formatted config file and returns its value
        :param section: [section] in the ini config to find this parameter
        :param key: The key in the provided section to look up
        :param default: Default value to return if nothing is found in the config.
        :param property: name of property to retrieve
        """
        try:
            if self.config.has_option(key.__objclass__.NAME.value, key.value):
                return self.config[key.__objclass__.NAME.value][key.value]
            else:
                return default
        except Exception as e:
            print(e)

    @staticmethod
    def figgy() -> "ConfigManager":
        """
        Get an instance of the figgy user provided configuration file
        """
        if not path.exists(CONFIG_OVERRIDE_FILE_PATH):
            with open(CONFIG_OVERRIDE_FILE_PATH, 'w') as figgy:
                figgy.write(EMPTY_CONFIG)

        return ConfigManager(CONFIG_OVERRIDE_FILE_PATH)
