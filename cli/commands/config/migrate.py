import stat

import consul
import hcl
from boto3.resources.base import ServiceResource

from commands.config_context import ConfigContext
from commands.types.config import ConfigCommand
from data.dao.ssm import SsmDao
from extras.s3_download_progress import S3Progress
from svcs.kms import KmsSvc
from utils.utils import *


class Migrate(ConfigCommand):

    def __init__(self, ssm_init: SsmDao, kms_init: KmsSvc, s3_resource: ServiceResource, colors_enabled: bool,
                 config_context: ConfigContext, config_completer: WordCompleter):
        super().__init__(migrate, colors_enabled, config_context)
        self._ssm = ssm_init
        self._kms = kms_init
        self._consul_type = None  # fetched after validation.
        self._consul_svc = None  # initialized after validation.
        self._ci_config_path = config_context.ci_config_path
        self._locals_path = config_context.locals
        self._s3_resource = s3_resource
        self._manual = config_context.manual
        self._namespace_suffix = ''
        self._utils = Utils(colors_enabled)
        self._config_completer = config_completer

        """
        self._consul_prefix is initalized from user data entry
        Consul prefix to migrate recursive underneath.
        If the prefix IS a single consul and has no children, that value will be migrated instead.
        """
        self._consul_prefix = None

    def _get_consul_keys(self, consul_prefix: str = "", dirs: bool = True) -> List:
        """
            Returns a list of keys in consul found beneath the passed in consul prefix
        Args:
            consul_prefix: Prefix to query consul key list from.

        Returns: List of found keys
        """
        try:
            result = self._consul_svc.kv.get(consul_prefix, recurse=True, keys=True)

            found_keys = result[1]
            if not dirs:
                found_keys = list(filter(lambda x: not x.endswith('/'), found_keys))
            return found_keys
        except (ConnectionError, ConnectTimeout) as e:
            print(e)
            self._utils.error_exit(
                "Are sure you have access to consul and are on the VPN? Unable to establish connection.")

    def _get_consul_prefix(self) -> str:
        """
        Prompts the user for a prefix to query Consul by. I.E. Api.Customers.
        Returns: The entered prefix.
        """
        print()
        print("You will need to supply a Consul prefix to find configs to migrate. "
              f"For instance {self.c.fg_bl}'Api.Customers'{self.c.rs} or {self.c.fg_bl}'Services.PM.Authorization'{self.c.rs}.")
        selection = prompt(f"Please input a consul prefix to query by: ",
                           completer=WordCompleter(self._get_consul_keys(), sentence=True))
        self._utils.validate(selection != '', "Invalid selection, please input a valid prefix.")
        return selection

    def _get_destination_prefix(self) -> str:
        """
        Prompts the user for a prefix to put all manually migrated configurations under.
        Returns: The entered prefix.
        """
        print()
        print("Please provide a prefix under which to migrate these keys in ParameterStore. I.E. /shared/mongo/")
        selection = ''
        notify = False
        while not self._utils.is_valid_input(selection, 'destination prefix', notify):
            selection = prompt(f"Please input a destination prefix : ",
                               completer=self._config_completer)
            notify = True

        return selection if selection.endswith('/') else f'{selection}/'

    def _get_namespace_suffix(self, service_name: str):
        """
        Prompts the user if they'd like to provide a namespace suffix to migrate configs under. Useful for versioning.
        Args:
            service_name: Service name that is being migrated.
        Returns: The selected suffix.

        """
        suffix = ''
        print()
        print(f"{self.c.fg_bl}Your current Parameter Store namespace is:{self.c.rs} {app_ns}/{service_name}/")
        print("During your migration you may append a namespace suffix. For instance if you'd like to convert your "
              "configurations to versioned configurations, a suffix of 'v1/' will migrate values selected in Consul "
              f"to the under the {app_ns}/{service_name}/v1/ prefix. e.g: {app_ns}/{service_name}/v1/some/value\r\n")
        selection = None
        notify = False
        while not self._utils.is_valid_selection(selection, notify):
            selection = input(f"Would you like to input a namespace suffix? (y/N): ")
            selection = selection if selection != '' else 'n'
            notify = True

        if selection.lower() == 'y':
            suffix = input(f"Please input your selected suffix: ")
            suffix = suffix if not suffix.startswith('/') else suffix[1:]
            suffix = suffix if suffix.endswith('/') else f'{suffix}/'
            print(f"Suffix selected: {suffix}")
            self._utils.validate(suffix != '', "Invalid selection, please input a valid suffix.")

        return suffix

    def _parse_locals(self) -> Dict:
        """
        Parses the locals.tf file and returns it as a DICT
        Returns: Dict with properties of locals.tf
        """
        with open(self._locals_path, 'r') as fp:
            contents = fp.read()

        return hcl.loads(contents)

    def _convert_json(self, consul_path) -> bool:
        """
        Prompts user on whether or not they would like to convert the detected json value into a K/V Heirarchy
        Args:
            consul_path: Location of the detected json
        """
        print()
        message = f"The consul value of {consul_path} is json. Would you like to convert it to a K/V heirarchy? (Y/N): "

        selection = ""
        while selection != 'y' and selection != 'n':
            selection = input(message).lower()

        return selection.lower() == 'y'

    def _migrate_json_to_ps(self, json_dict: Dict, ps_prefix: str, migrated_list: List[str] = [],
                            consul_path: str = None) -> List[str]:
        """
        Recursively migrates a passed in dictionary (which originated from json) into Parameter store.
        Args:
            json_dict:
            ps_prefix: The prefix to store values found in this section in parameter store. This changes based on how
            deep down the tree of json the value is.
            migrated_list: This is passed through recursively to assemble a list of successfully migrated values that is
            aggregated and returned.

        Returns:

        """
        for key, value in json_dict.items():
            if isinstance(value, dict):
                self._migrate_json_to_ps(value, f'{ps_prefix}/{key}',
                                         migrated_list=migrated_list, consul_path=f'{consul_path}/{key}')
            else:
                print(f"{self.c.fg_gr}Storing in PS:{self.c.rs} {self.c.fg_bl}{ps_prefix}/{key}{self.c.rs}")
                self._store_value(f'{ps_prefix}/{key}', str(value), consul_path)
                migrated_list.append(f'{ps_prefix}/{key}')

        return migrated_list

    def _migrate_consul_value(self, consul_path: str, ps_path: str) -> List[str]:
        """
        Migrates a consul value into PS. If that value is detected as a JSON blob, the user is prompted if they'd like to
        store it directly as json or to convert it to many PS values.
        Args:
            consul_path: /path/to/kv/pair/in/consul
            ps_path: /destination/in/ps/value
        Returns:

        """
        migrated_keys = []
        try:
            if self._is_consul_value(consul_path):
                result = self._consul_svc.kv.get(consul_path)
                value = str(result[1]['Value'], 'utf-8')
                if Utils.is_json(value) and self._convert_json(consul_path):
                    migrated_keys = migrated_keys + self._migrate_json_to_ps(json.loads(value), ps_path,
                                                                             consul_path=consul_path)
                else:
                    if Utils.str_too_long(value) and Utils.is_json(value):
                        print()
                        print(
                            f"The json blob stored at {consul_path} is too large to be stored in ParameterStore. "
                            f"It's a good idea to consider converting it to a K/V Heirarchy!")
                        print()
                        migrated_keys = migrated_keys + self._migrate_key(consul_path, ps_path, migrated_keys)
                    elif Utils.str_too_long(value) and not Utils.is_json(value):
                        print(
                            f"{self.c.fg_rd}The value stored at {self.c.rs}{self.c.fg_bl}{consul_path}{self.c.rs}{self.c.fg_rd} "
                            f"is simply too large!  It cannot be transitioned to PS as is. You will have to break it "
                            f"apart manually.{self.c.rs}")
                    else:
                        self._store_value(ps_path, value, consul_path)
                        migrated_keys.append(ps_path)

            return migrated_keys
        except ConnectionError:
            self._utils.error_exit(
                "Are sure you have access to consul and are on the VPN? Unable to establish connection.")

    def _store_value(self, ps_path, value, consul_path) -> None:
        """
        Stores
        Args:
            ps_path: Path in parameter store to store the value
            value: The value itself
            consul_path: The source location where the value originated in Consul.
        """
        ps_type = SSM_STRING

        if value.startswith(LEGACY_KMS_ENCRYPTION_PREFIX):
            self._safe_install_decrypter()
            decrypter = DECRYPTER_WIN_FILE_PATH if self._utils.is_windows() else DECRYPTER_FILE_PATH
            print(f"{self.c.fg_bl}Legacy encrypted value detected, attempting decryption for {consul_path}.{self.c.rs}")
            value = str(subprocess.check_output([decrypter, f'{self.run_env}', f'{self.role}', value]),
                        'utf-8').strip()
            ps_type = SSM_SECURE_STRING
        elif self._kms.is_encrypted(value):
            value = self._kms.decrypt(value)
            ps_type = SSM_SECURE_STRING

        if self._utils.is_valid_input(value, consul_path, False):
            self._ssm.set_parameter(ps_path, value, f"Migrated from {consul_path}.", ps_type)
        else:
            print(f"Unable to migrate {self.c.fg_rd}{consul_path}{self.c.rs}, it's value is empty or None. "
                  f"Parameters cannot be empty.")

    def _safe_install_decrypter(self) -> None:
        """
        Safely installs the decrypter plugin to the figgy so we can decrypt legacy toolbox-encrypted consul values.
        """
        s3_path_prefix = f'{DECRYPTER_S3_PATH_PREFIX}{self._utils.get_os()}'
        if not self._utils.file_exists(DECRYPTER_WIN_FILE_PATH) and not self._utils.file_exists(DECRYPTER_FILE_PATH):
            s3_suffix = ".exe" if self._utils.is_windows() else ""
            dest = DECRYPTER_WIN_FILE_PATH if self._utils.is_windows() else DECRYPTER_FILE_PATH
            print(f"You're missing a necessary decryption module required. "
                  f"Installing legacy decryption module in your ~/.figgy/devops/ directory.")
            s3_file = f'{s3_path_prefix}/decrypt{s3_suffix}'
            self._s3_file = s3_file
            total_bytes = self._s3_resource.Object(CLI_BUCKET, s3_file).content_length
            progress = S3Progress(total=total_bytes, unit='B', unit_scale=True, miniters=1, desc='Downloading')
            bucket = self._s3_resource.Bucket(CLI_BUCKET)

            with progress:
                bucket.download_file(s3_file, dest, Callback=progress)

            st = os.stat(dest)
            os.chmod(dest, st.st_mode | stat.S_IEXEC)
            print(f"{self.c.fg_gr}Installation complete.{self.c.rs}")

    def _print_found_keys(self, keys: List):
        """
        Pretty prints out all found keys in Consul from the provided Prefix.
        Args:
            keys: The list of found keys
        """
        print()
        print(f"The following keys were found in consul under the provided path: {self._consul_prefix}")
        for key in keys:
            print(f'{self.c.fg_bl}{key}{self.c.rs}')

    def _confirm_continue_with_selected_keys(self, dest_prefix: str) -> None:
        """
        Prompts user to confirm that they want to continue with the printed out key selections
        Args:
            dest_prefix: The prefix to prepend to the destination path.
            run_env: run environment
        """

        print(f"\r\nThese keys and their values will be migrated into the {self.c.fg_rd}*{self.run_env}*{self.c.rs} "
              f"Parameter Store under the {self.c.fg_bl}{dest_prefix}{self._namespace_suffix}{self.c.rs} namespace.")
        start_valid = True
        selection = ""
        while start_valid or not self._utils.is_valid_selection(selection, notify=False):
            selection = prompt("Would you like to continue? (Y/n): ").strip().lower()
            selection = selection if selection != '' else 'y'
            start_valid = False

        if selection == 'n':
            exit(0)

    def _select_manual_key(self):
        print()
        found_keys = self._get_consul_keys(dirs=False)
        selection = prompt(f"Select a Consul key to migrate: ",
                           completer=WordCompleter(found_keys, sentence=True))
        self._utils.validate(selection != '' and not selection.endswith('/'),
                             "Invalid selection, please input a valid key.")
        return selection

    def _select_ps_destination(self):
        shared_completer = self._config_completer
        # Filter out all namespaces that are not shared from previously initialized completer (more efficient)
        shared_completer.words = list(filter(lambda x: x.startswith(shared_ns), shared_completer.words))

        print()
        selection = prompt(f"Please enter a PS destination. ",
                           completer=shared_completer)
        self._utils.validate(selection != '' and not selection.endswith('/'),
                             "Invalid selection, please input a valid key.")
        return selection

    def _migrate_key(self, key: str, ps_name: str, migrated_keys: List[str] = []) -> List[str]:
        """
        Migrates a single consul key to PS. This can be called somewhat recursively from within the migrate_consul_key()
        method. If this is done, we pass in the already migrated_keys as a list, and append them to the list curated here.
        This way we can always keep track of the consul keys that are migrated during json -> K/V Hierarchy conversion.
        Args:
            key: Consul Key
            ps_name: PS Destination
            migrated_keys: Any keys we want to add to the returned key list. Useful for recursive calls

        Returns:

        """
        print()
        print(f"Source: {key}")
        print(f"Dest:   {ps_name}")
        selection = prompt(f"Migrate? (Y/n): ").strip().lower()
        selection = selection if selection != '' else 'y'
        if selection == 'y':
            migrated_keys = migrated_keys + self._migrate_consul_value(key, ps_name)
            return migrated_keys

        return migrated_keys

    def _migrate_keys(self, destination_prefix: str, keys: List) -> List:
        """
        Migrates a set of consul keys provided to parameter store. If a key's value is JSON, a user will be prompted to
        convert to a K/V Hierarchy
        Args:
            destination_prefix: /app/service-name/ in most cases. The prefix to apply to all migrated keys
            keys: List of consul Keys to migrate

        Returns: A list PS parameter names of migrated key locations. Includes keys if a json blob was converted to
        many PS parameters
        """
        migrated_keys = []
        prefix_is_value = self._is_consul_value(self._consul_prefix)

        for key in keys:
            if prefix_is_value:
                key_suffix = self._consul_prefix.split('/')[-1]
            else:
                key_suffix = key.replace(self._consul_prefix, "")

            key_suffix = key_suffix if not key_suffix.startswith('/') else key_suffix[1:]
            ps_name = f'{destination_prefix}{self._namespace_suffix}{key_suffix}'
            migrated_keys = migrated_keys + self._migrate_key(key, ps_name)

        return migrated_keys

    def _migrate_arbitrary_consul_path(self, ssm_prefix, run_env: RunEnv, consul_type: str):
        consul_svc = consul.Consul(host=consul_map[run_env.env][consul_type], port=consul_port)
        found_keys = []
        try:
            result = consul_svc.kv.get(self._consul_prefix, recurse=True, keys=True)
            found_keys = result[1]
        except (ConnectionError, ConnectTimeout) as e:
            print(e)
            self._utils.error_exit("Are sure you have access to consul and are on the VPN? Unable to establish "
                                   "connection.")

        print(f"Found keys: {found_keys}")
        keys_no_dirs = list(filter(lambda x: not x.endswith('/'), found_keys))
        migrated_keys = []
        new_ps_keys = []
        for key in keys_no_dirs:
            ps_type = SSM_STRING
            result = consul_svc.kv.get(key)
            ps_name = key.replace(self._consul_prefix, ssm_prefix)
            print(f"Fetching {key}")
            if result is not None and result[1] is not None and 'Value' in result[1] and result[1]['Value'] is not None:
                value = str(result[1]['Value'], 'utf-8')
                if LEGACY_KMS_ENCRYPTION_PREFIX in value:
                    decrypter = DECRYPTER_WIN_FILE_PATH if self._utils.is_windows() else DECRYPTER_FILE_PATH
                    print(f"Legacy encrypted value detected, attempting decryption for {key}.")
                    value = str(subprocess.check_output([decrypter, f'{run_env}', f'{self.role.role}', value]),
                                'utf-8').strip()
                    ps_type = SSM_SECURE_STRING

                print(f"{ps_name} : {value}")
                self._ssm.set_parameter(ps_name, value, f"Migrated from {key}.", ps_type)
                migrated_keys.append(key)
                new_ps_keys.append(ps_name)

    # This has been deprecated and is no longer used, it was used for single KV migrations but has been replaced
    # for K/V hierarchies (if only one)
    def _migrate_single(self):
        """
        Manages manual migrations of a single key, or a K/V hierarchy.
        """
        do_more = True
        while do_more:
            try:
                consul_path = self._select_manual_key()
                ps_path = self._select_ps_destination()
                self._utils.validate(ps_path.startswith(shared_ns) or ps_path.startswith(app_ns),
                                     f"You may only migrate consul keys into the {app_ns} or {shared_ns} PS namespaces.")
                result = self._consul_svc.kv.get(consul_path)
                self._utils.validate(len(result) > 0, f"No consul value found at path {consul_path}.")
                value = str(result[1]['Value'], 'utf-8')
                self._store_value(ps_path, value, consul_path)
                print(f"Successfully migrated: {self.c.fg_bl}{consul_path}{self.c.rs} -> "
                      f"{self.c.fg_bl}{ps_path}{self.c.rs}\r\n")
                selection = prompt("Migrate Another? (Y/n): ").strip().lower()
                selection = selection if selection != '' else 'y'
                do_more = selection.lower() == 'y'
            except ConnectionError:
                self._utils.error_exit(
                    "Are sure you have access to consul and are on the VPN? Unable to establish connection.")

    def _is_consul_value(self, consul_path):
        result = self._consul_svc.kv.get(consul_path)
        if result and result[1] and 'Value' in result[1] \
                and result[1]['Value'] != '' and result[1]['Value'] is not None:
            return True

        return False

    def _migrate_manual(self):
        """
        Orchestrates manually migrating 1 -> N parameters from Consul to PS
        """
        self._consul_prefix = self._get_consul_prefix()
        destination_prefix = self._get_destination_prefix()
        found_keys = self._get_consul_keys(self._consul_prefix)
        self._utils.validate(found_keys and len(found_keys) > 0,
                             "Your query returned no keys in consul. Please select a valid consul prefix.")
        keys_no_dirs = list(filter(lambda x: not x.endswith('/'), found_keys))
        self._print_found_keys(keys_no_dirs)
        self._confirm_continue_with_selected_keys(destination_prefix)

        self._migrate_keys(destination_prefix, keys_no_dirs)

    def _migrate_kv_hierarchy(self, service_name: str) -> None:
        """
        Orchestrates the migration of parameters from Consul to PS for one ENV of a project
        Args:
            service_name: service_name as defined in the locals.tf
        """

        self._consul_prefix = self._get_consul_prefix()
        found_keys = self._get_consul_keys(self._consul_prefix)
        self._utils.validate(found_keys and len(found_keys) > 0,
                             "Your query returned no keys in consul. Please select a valid consul prefix.")
        keys_no_dirs = list(filter(lambda x: not x.endswith('/'), found_keys))
        self._print_found_keys(keys_no_dirs)
        self._namespace_suffix = self._get_namespace_suffix(service_name)
        self._confirm_continue_with_selected_keys(f'{app_ns}/{service_name}/')
        migrated_list = self._migrate_keys(f'{app_ns}/{service_name}/', keys_no_dirs)

        config = self._utils.get_ci_config(self._ci_config_path)
        config[CONFIG_KEY] = list(dict.fromkeys(config[CONFIG_KEY] + migrated_list))  # Maintains order by dedupes

        print(f"\r\nUpdating {self._ci_config_path} with newly added parameters.")
        with open(self._ci_config_path, 'w') as file:
            json.dump(config, file, indent=4, sort_keys=True)

        print(
            f"{self.c.bl}Your ci-config.json file at {self._ci_config_path} has been updated with the migrated paths.{self.c.rs}")
        print(f"{self.c.fg_gr}Migration complete.{self.c.rs}")

    def execute(self):

        # Validate & parse ci-config.json
        # There are issues parsing locals.tf with the HCL lib on windows - so opting for regex for now.
        # if self._utils.is_windows():
        self._utils.validate(self._manual or (self._locals_path and self._ci_config_path),
                             "If you are attempting to migrating K/V pairs one at a time you must provide the `--manual` flag. "
                             "Otherwise, if you are attempting to migrate a Consul K/V Hiearchy (many keys at once), you must "
                             "provide paths to your project's configurations through the `--config` and `--locals` parameters.")
        self._utils.validate(self._locals_path and self._locals_path.endswith('locals.tf') or self._manual,
                             'File provided for --locals parameter MUST be named `locals.tf`')

        self._consul_type = self._utils.get_consul_type()
        self._consul_svc = consul.Consul(host=consul_map[self.run_env.env][self._consul_type], port=consul_port)

        if self._manual:
            self._migrate_manual()
        else:
            with open(self._locals_path, 'r') as fp:
                contents = fp.read()
                base_matcher = re.search(r'^.*service_name.*=.*[\'|"]([A-Za-z0-9-_*]+)[\'|"].*$',
                                         contents, re.MULTILINE)

                self._utils.validate(base_matcher.group() is not None,
                                     "Failure parsing your service_name from the provided "
                                     "locals.tf. Are you sure it has a service_name defined?")
                service_name = base_matcher.group(1)

            self._migrate_kv_hierarchy(service_name)
