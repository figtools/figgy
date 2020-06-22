import json
import logging
import os
import platform
import re
import time
from collections import OrderedDict
from json.decoder import JSONDecodeError
from pathlib import Path
from sys import exit
from typing import Dict, List, Union

import botocore
import urllib3

from figcli.config import *
from figcli.config.style.color import Color
from figcli.config.style.terminal_factory import TerminalFactory

log = logging.getLogger(__name__)

BACKOFF = .25
MAX_RETRIES = 10


class Utils:

    def __init__(self, colors_enabled=False):
        self.c = TerminalFactory(colors_enabled).instance().get_colors()

    @staticmethod
    def retry(function):
        """
        Decorator that supports automatic retries if connectivity issues are detected with boto or urllib operations
        """

        def inner(self, *args, **kwargs):
            retries = 0
            while True:
                try:
                    return function(self, *args, **kwargs)
                except (botocore.exceptions.EndpointConnectionError, urllib3.exceptions.NewConnectionError) as e:
                    print(e)
                    if retries > MAX_RETRIES:
                        raise e

                    self._utils.notify("Network connectivity issues detected. Retrying with back off...")
                    retries += 1
                    time.sleep(retries * BACKOFF)

        return inner

    @staticmethod
    def trace(func):
        """
        Decorator that adds logging around function execution and function parameters.
        """

        def wrapper(*args, **kwargs):
            log.info(f"Entering function: {func.__name__} with args: {args}")
            start = time.time()
            result = func(*args, **kwargs)
            log.info(f"Exiting function: {func.__name__} and returning: {result}")
            log.info(f"Function complete after {round(time.time() - start, 2)} seconds.")
            return result

        return wrapper

    @staticmethod
    def millis_since_epoch():
        return int(time.time() * 1000)

    @staticmethod
    def get_os():
        return platform.system().lower()

    @staticmethod
    def not_windows():
        return platform != WINDOWS

    @staticmethod
    def is_linux():
        return platform.system() == LINUX

    @staticmethod
    def is_mac():
        return platform.system() == MAC

    @staticmethod
    def is_windows():
        return platform.system() == WINDOWS

    @staticmethod
    def find_figgy_json():
        for path in DEFAULT_FIGGY_JSON_PATHS:
            if Path(path).is_file():
                return path

        return 'figgy.json'

    @staticmethod
    def file_exists(path: str):
        return Path(path).is_file()

    @staticmethod
    def is_set_true(attr: frozenset, args) -> bool:
        attr_name = Utils.clean_attr_name(attr)

        if hasattr(args, attr_name):
            return args.__dict__.get(attr_name, False)
        else:
            return False

    @staticmethod
    def command_set(check_command: frozenset, args):
        command_name = args.command if hasattr(args, Utils.get_first(command)) else None

        return command_name == Utils.get_first(check_command)

    @staticmethod
    def attr_if_exists(attr: frozenset, args, default=None) -> Union[object, None]:
        attr_name = Utils.clean_attr_name(attr)
        return args.__dict__.get(attr_name, default)

    @staticmethod
    def attr_exists(attr: frozenset, args) -> bool:
        attr_name = Utils.clean_attr_name(attr)
        return args.__dict__.get(attr_name, None) is not None

    @staticmethod
    def clean_attr_name(attr: frozenset) -> str:
        return Utils.get_first(attr).replace('-', '_')

    @staticmethod
    def sanitize_session_name(name: str):
        return re.sub(r'\W+', '', name)[:15]


    @staticmethod
    def wipe_defaults():
        try:
            os.remove(DEFAULTS_FILE_CACHE_PATH)
        except OSError:
            pass

    @staticmethod
    def wipe_config_cache():
        try:
            os.remove(CONFIG_CACHE_FILE_PATH)
        except OSError:
            pass

    @staticmethod
    def wipe_vaults():
        for file in FIGGY_VAULT_FILES:
            try:
                os.remove(file)
            except OSError:
                pass

    def notify(self, message: str):
        print(f'{self.c.fg_bl}{message}{self.c.rs}')

    def merge_config_contents(self, a: Dict, b: Dict, a_path: str, b_path: str):
        for key in b:
            if isinstance(b[key], dict):
                if key in b and key in a:
                    dupes = b[key].keys() & a[key].keys()
                    self.validate(dupes == set(), f"Duplicate keys found between your configs. You may not have "
                                                  f"two instances of {key} with overlapping keys. Culprits: {dupes}")

                a_key = a[key] if key in a else {}
                b_key = b[key] if key in b else {}
                a[key] = {**a_key, **b_key}

            elif isinstance(b[key], list):
                a_key = a[key] if key in a else []
                b_key = b[key] if key in b else []
                a[key] = a_key + b_key
            else:
                self.error_exit(f"Unable to merge config values of type: {type(b[key])} for "
                                f"specified key {key} in both {a_path} and {b_path}")

        return a

    def get_repl_config(self, repl_config_path: str):
        with open(repl_config_path, "r") as file:
            contents = file.read()
            self.validate(contents != '', f"File provided at: {repl_config_path} "
                                          f"cannot be empty.")
            self.validate(self.is_json(contents), "File provided contains invalid json. Please remediate.")
            conf = json.loads(contents)
            self.validate(REPLICATION_KEY in conf, f"{REPLICATION_KEY} is missing from replication config: "
                                                   f"{repl_config_path}. This file is invalid.")
            return self.get_config_key_safe(REPLICATION_KEY, conf, default=[])

    def get_ci_config(self, ci_config_path: str) -> Dict:
        self.validate(ci_config_path.endswith('.json'),
                      "The figgy config file must end with the extension '.json'. A name of `figgy.json` is "
                      "recommended for most use cases..")

        self.validate(os.path.exists(ci_config_path), f"Path {ci_config_path} is invalid. That file does not exist.")

        # Read & Validate figgy.json
        try:
            with open(ci_config_path, "r") as file:
                base_matcher = re.search('^(.*[/]*).*.json$', ci_config_path)
                base_path = base_matcher.group(1)
                contents = file.read()
                self.validate(contents != '',
                              f"File provided at: {self.c.fg_rd}{ci_config_path}{self.c.rs} cannot be empty.")
                ci_config = json.loads(contents, encoding='utf-8')

                if IMPORTS_KEY in ci_config:
                    for import_val in ci_config[IMPORTS_KEY]:
                        import_path = f"{base_path}/{import_val}"
                        print(f"Loading imported config: {import_path}")
                        with open(import_path) as import_file:
                            contents = import_file.read()
                            imported_config = json.loads(contents)
                            ci_config = self.merge_config_contents(ci_config, imported_config, ci_config_path,
                                                                   import_path)

                namespace = self.get_namespace(ci_config)
                app_figs = self.get_config_key_safe(CONFIG_KEY, ci_config, default=[])
                dupes = self.find_dupes(app_figs)
                self.validate(not dupes, f"Your configuration has duplicate keys: {self.c.fg_rd}{dupes}{self.c.rs}")

                ns_app_params = self.standardize_parameters(namespace, app_figs)
                ci_config[CONFIG_KEY] = ns_app_params

                ns_shared_params = self.standardize_parameters(namespace,
                                                               self.get_config_key_safe(SHARED_KEY, ci_config,
                                                                                        default=[]))
                ci_config[SHARED_KEY] = ns_shared_params

                dupes = self.find_dupes(list(self.get_config_key_safe(REPLICATION_KEY, ci_config, default={}).values()))
                self.validate(not dupes, f"Your configuration has duplicate values in your replicated values "
                                         f"config: {self.c.fg_rd}{dupes}{self.c.rs}")

                self.validate(
                    len(self.get_config_key_safe(CONFIG_KEY, ci_config, default=[])) > 0
                    or OPTIONAL_NAMESPACE in ci_config, f"If you have no defined Names under: {CONFIG_KEY} you must "
                                                        f"specify an {OPTIONAL_NAMESPACE} parameter instead with a "
                                                        f"value of '/app/your-service-name/'")

                return ci_config

        except json.decoder.JSONDecodeError as e:
            print(f"{self.c.fg_rd}Error decoding json in figgy.json. Invalid JSON detected. "
                  f"Caught error: {e}{self.c.rs}")
            exit(1)
        except FileNotFoundError as e:
            print(f"{self.c.fg_rd}File at path {ci_config_path} does not exist or could not be read. "
                  f"Are you sure you provided a valid file path?{self.c.rs}")
            exit(1)

    def standardize_parameters(self, namespace: str, params: List[str]) -> List[str]:
        standardized = []
        for param in params:
            if not param.startswith(namespace):
                if param.startswith("/"):
                    standardized.append(f'{namespace}{param[1:]}')  # just in case they have an extra / by accident.
                else:
                    standardized.append(f'{namespace}{param}')
            else:
                standardized.append(param)

        return standardized

    def get_namespace(self, config: Dict):
        if OPTIONAL_NAMESPACE in config:
            namespace = config[OPTIONAL_NAMESPACE]
        else:
            self.validate(CONFIG_KEY in config, f"You must specify an {CONFIG_KEY} or {OPTIONAL_NAMESPACE} block, "
                                                f"or both, in your figgy.json file.")
            namespace = self.parse_namespace(self.get_first(set(config[CONFIG_KEY])))

        self.validate(namespace is not None, f"Invalid namespace provided, or unable to parse valid "
                                             f"namespace from your {CONFIG_KEY} block.")
        if not namespace.endswith('/'):
            namespace = namespace + '/'

        return namespace

    def get_service_name(self, config: Dict):
        namespace = self.get_namespace(config)
        return namespace.split('/')[2]

    @staticmethod
    def get_parameter_only(parameter_name: str):
        base_name = parameter_name
        """
        Takes /app/foo/a/full/path and returns a/full/path and always removes the namespace if it exists.
        :param parameter_name: name of a parameter, with or without the namespace.
        :return: parameter/name/path without any attached namespace.
        """
        try:
            get_param = re.compile(r"^/app/[A-Za-z0-9_-]+/(.*)")
            result = get_param.match(parameter_name)
            base_name = result.group(1)
        except (AttributeError, TypeError) as e:
            Utils.stc_error_exit(f"Unable to detect base name for parameter: {parameter_name}. {e}")

        return base_name

    @staticmethod
    def parse_namespace(app_key: str) -> str:
        ns = None
        try:
            get_ns = re.compile(r"^(/app/[A-Za-z0-9_-]+/).*")
            val = get_ns.match(app_key)
            ns = val.group(1)
        except (AttributeError, TypeError) as e:
            print(f"Unable to parse namespace from {app_key}. If your app_figs block values do not begin with "
                  f"the prefix /app/your-service-name , you must include the 'namespace' property in your figgy.json "
                  f"with value /app/your-service-name/")

        return ns

    def find_dupes(self, lst: List):
        return [x for n, x in enumerate(lst) if x in lst[:n]]

    def error_exit(self, error_msg: str):
        print(f"{self.c.fg_rd}ERROR: >> {error_msg}{self.c.rs}")
        exit(1)

    @staticmethod
    def stc_error_exit(error_msg: str):
        print(f"ERROR: >> {error_msg}")
        exit(1)

    @staticmethod
    def write_error(file_name: str, error_message: str):
        with open(f'{ERROR_LOG_DIR}/{file_name}', "w+") as log:
            log.write(error_message)

    @staticmethod
    def stc_validate(boolean: bool, error_msg: str):
        if not boolean:
            Utils().error_exit(error_msg)

    def validate(self, boolean: bool, error_msg: str):
        if not boolean:
            self.error_exit(error_msg)


    def is_valid_selection(self, selection: str, notify: bool):
        result = selection is not None and (selection.lower() == "y" or selection.lower() == "n")
        if notify and not result:
            msg = f"You must input a selection of 'Y' or 'N'"
            print(f"{self.c.fg_rd}{msg}{self.c.rs}")
        return result

    def is_valid_input(self, input: str, field_name: str, notify: bool):
        result = input is not None and input != ""
        if notify and not result:
            msg = f"ERROR: Your input of >> {input} << is not valid for {field_name}. " \
                  f"You cannot input an empty string or None"
            print(f"{self.c.fg_rd}{msg}{self.c.rs}")
        return result

    @staticmethod
    def stc_is_valid_input(input: str, field_name: str, notify: bool):
        result = input is not None and input != ""
        if notify and not result:
            msg = f"ERROR: Your input of >> {input} << is not valid for {field_name}. " \
                  f"You cannot input an empty string or None"
            print(f"{msg}")
        return result

    @staticmethod
    def format_config(config: Dict) -> OrderedDict:
        """
        Takes a formatted figgy.json file dictionary and converts it to an ordered dictionary. This makes it possible
        to write the file back out as a more readable and logically formatted file.
        """

        ordered_config = OrderedDict()

        if config.get(SERVICE_KEY):
            ordered_config[SERVICE_KEY] = config.get(SERVICE_KEY)

        if config.get(PLUGIN_KEY):
            ordered_config[PLUGIN_KEY] = config.get(PLUGIN_KEY)

        if config.get(OPTIONAL_NAMESPACE):
            ordered_config[OPTIONAL_NAMESPACE] = config.get(OPTIONAL_NAMESPACE)

        if config.get(IMPORTS_KEY):
            ordered_config[IMPORTS_KEY] = config.get(IMPORTS_KEY)

        ordered_config[CONFIG_KEY] = config.get(CONFIG_KEY, [])

        if config.get(REPL_FROM_KEY):
            ordered_config[REPL_FROM_KEY] = config.get(REPL_FROM_KEY)

        if config.get(REPLICATION_KEY):
            ordered_config[REPLICATION_KEY] = config.get(REPLICATION_KEY)

        if config.get(MERGE_KEY):
            ordered_config[MERGE_KEY] = config.get(MERGE_KEY)

        if config.get(SHARED_KEY):
            ordered_config[SHARED_KEY] = config.get(SHARED_KEY)

        return ordered_config

    @staticmethod
    def get_first(some_set: Union[set, frozenset]):
        if some_set:
            return set(some_set).pop()

        return None

    @staticmethod
    def str_too_long(value: str) -> bool:
        """
        Is this string too log to store in PS?
        Args:
            value: string to count

        Returns: bool
        """
        return len(value) > 4096

    @staticmethod
    def is_json(obj: str) -> bool:
        """
        Take a string and returns whether or not it is parseable as json.
        Args:
            obj: String to check

        Returns: True/False
        """
        try:
            json.loads(obj)
        except JSONDecodeError:
            return False

        # json.loads considers "true" or "false" valid json, but it's not valid in our case..
        if obj == "true" or obj == "false":
            return False

        # If it's a basic array, nope!
        if obj.startswith('[') and obj.endswith(']'):
            return False

        # json.loads considers strings that are numbers, valid json.
        try:
            int_obj = int(obj)
            if int_obj:
                return False
        # Do nothing if we catch an exception, That means this is json!
        except (NameError, ValueError):
            # json.loads considers strings that are numbers, valid json.
            try:
                fl_obj = float(obj)
                if fl_obj:
                    return False
            # Do nothing if we catch an exception, That means this is json!
            except (NameError, ValueError):
                return True

        return True

    @staticmethod
    def chunk_list(lst: List, chunk_size: int) -> List[List]:
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(lst), chunk_size):
            yield lst[i:i + chunk_size]

    @staticmethod
    def parse_bool(value: Union[str, bool]) -> bool:
        if isinstance(value, bool):
            return bool(value)

        value = value.replace("'", '').replace('"', '').strip()
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        else:
            raise ValueError(f"Provided bool value of {value} is not a valid bool type.")

    @staticmethod
    def default_colors(enabled: bool = None) -> Color:
        if enabled is None:
            enabled = Utils.not_windows()

        return TerminalFactory(enabled).instance().get_colors()

    @staticmethod
    def to_env_var(variable_name: str):
        """
        converts aCasedVarable to A_CASED_VARIABLE case.
        """
        str1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', variable_name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', str1).upper()

    def get_config_key_safe(self, key: str, config: Dict, default=None):
        if key in config:
            return config[key]
        else:
            if default is None:
                return []
            else:
                return default


class InvalidSessionError(Exception):
    pass
