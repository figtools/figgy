import re
from typing import *

from botocore.exceptions import ClientError

from figcli.commands.config.get import Get
from figcli.commands.config.put import Put
from figcli.commands.config_context import ConfigContext
from figcli.commands.types.config import ConfigCommand
from figcli.data.dao.config import ConfigDao
from figcli.data.dao.ssm import SsmDao
from figcli.extras.key_utils import KeyUtils
from figcli.models.replication_config import ReplicationConfig, ReplicationType
from figcli.config import *
from figcli.svcs.observability.anonymous_usage_tracker import AnonymousUsageTracker
from figcli.svcs.observability.version_tracker import VersionTracker
from figcli.utils.utils import Utils


class Sync(ConfigCommand):

    def __init__(self, ssm_init: SsmDao, config_init: ConfigDao, colors_enabled: bool,
                 context: ConfigContext, get: Get, put: Put):
        super().__init__(sync, colors_enabled, context)
        self._config = config_init
        self._ssm = ssm_init
        self._config_path = context.ci_config_path if context.ci_config_path else Utils.find_figgy_json()
        self._utils = Utils(colors_enabled)
        self._replication_only = context.replication_only
        self._errors_detected = False
        self.example = f"{self.c.fg_bl}{CLI_NAME} config {self.command_printable} " \
                       f"--env dev --config /path/to/config{self.c.rs}"
        self._get: Get = get
        self._put: Put = put
        self._FILE_PREFIX = "file://"

    def _load_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            self._utils.error_exit(f"Provided file path: {file_path} is invalid. No file found.")

    def _input_config_values(self, config_keys: Set[str]) -> None:
        """
        Prompts the user for each of the passed in set of config values if any are missing from PS.
        :param config_keys: Set[string] - config values to prompt the user to add.
        """

        def validate_msg(ps_name: str):
            print(f"Name Validated: {self.c.fg_bl}{ps_name}{self.c.rs}")
            return validate_msg

        count = 0
        for key in config_keys:
            try:
                if not self._get.get(key):
                    print(f"Name {self.c.fg_bl}{key}{self.c.rs} does not exist in ParameterStore for the "
                          f"{self.c.fg_bl}{self.run_env}{self.c.rs} environment. It must be added before this "
                          f"build can continue.\n")
                    self._put.put_param(key=key, display_hints=count == 0)
                    count = count + 1
                else:
                    validate_msg(key)
            except ClientError:
                validate_msg(key)

        if count:
            print(f"{self.c.fg_bl}{count} {'value' if count == 1 else 'values'} added successfully{self.c.rs}")

    def _sync_keys(self, config_namespace: str, all_keys: Set):
        """
        Looks for orphaned parameters (keys) under the namespace provided and prints out information about
        missing parameters that are not defined in the figgy.json file
        Args:
            config_namespace: Namespace to query PS under.
            all_keys: All keys that exist in figgy.json to compare against.
        """
        print(f"{self.c.fg_gr}Checking for orphaned config names.{self.c.rs}")

        # Find & Cleanup orphaned keys
        ps_keys = set(list(map(lambda x: x['Name'], self._ssm.get_all_parameters([config_namespace]))))
        ps_only_keys = ps_keys.difference(all_keys)

        if len(ps_only_keys) > 0:
            print(UNUSED_CONFIG_DETECTED.replace("%%red%%", self.c.fg_rd)
                  .replace("%%blue%%", self.c.fg_bl)
                  .replace("%%rs%%", self.c.rs))

        for key in ps_only_keys:
            print(f"Unused Parameter: {self.c.fg_bl}{key}{self.c.rs}")

        if not ps_only_keys:
            print(f"{self.c.fg_bl}No orphaned names found.{self.c.rs}")

    def _sync_repl_configs(self, config_repl: Dict, namespace: str = None) -> None:
        """
        Syncs replication configs from a defined "replicate_figs" block parsed from either the figgy.json file
        or the data replication config json file.
        Args:
            config_repl: Dict of KV Pairs for a repl config. Source -> Dest
            namespace: Optional namespace. Parsed from destination if not supplied.
        """
        local_configs: List[ReplicationConfig] = ReplicationConfig.from_dict(conf=config_repl,
                                                                             type=ReplicationType(REPL_TYPE_APP),
                                                                             run_env=self.run_env, namespace=namespace)
        for l_cfg in local_configs:
            # Namespace will be missing for --replication-only syncs. Otherwise, with standard syncs, namespace is passed
            # as a parameter here.
            if not namespace:
                namespace = l_cfg.namespace

            if not l_cfg.destination.startswith(namespace):
                print(f"{self.c.fg_rd}Replication config {l_cfg.source} -> {l_cfg.destination} has a destination that "
                      f"is not in your service namespace: {namespace}. This is invalid.{self.c.rs}")
                self.errors_detected = True
                continue

            remote_cfg = self._config.get_config_repl(l_cfg.destination, self.run_env)

            # Should never happen, except when someone manually deletes source / destination without going through CLI
            missing_from_ps = self._ssm.get_parameter_encrypted(l_cfg.source) is None

            if not remote_cfg or remote_cfg != l_cfg or missing_from_ps:
                try:
                    if self._can_replicate_from(l_cfg.source) and not remote_cfg or missing_from_ps:
                        self._config.put_config_repl(l_cfg)
                        print(f"{self.c.fg_gr}Replication added:{self.c.rs} {l_cfg.source} -> {l_cfg.destination}")
                    elif self._can_replicate_from(l_cfg.source) and remote_cfg:
                        self._config.put_config_repl(l_cfg)
                        print(f"{self.c.fg_bl}Replication updated.{self.c.rs}")
                        print(f"{self.c.fg_rd}Removed: {remote_cfg.source} -> {remote_cfg.destination}")
                        print(f"{self.c.fg_gr}Added: {l_cfg.source} -> {l_cfg.destination}")
                    else:
                        self._errors_detected = True
                        # print(f"{self.c.fg_rd}You do not have permission to configure replication from source:"
                        #       f"{self.c.rs} {key}")
                except ClientError:
                    self._utils.validate(False, f"Error detected when attempting to store replication config "
                                                f"for {l_cfg.destination}")
                    self._errors_detected = True
            else:
                print(f"{self.c.fg_bl}Replication Validated:{self.c.rs} {l_cfg.source} -> {l_cfg.destination}")

    def _notify_of_data_repl_orphans(self, config_repl: Dict) -> None:
        """
        Notify user of detected orphaned replication configurations when using the --replication-only flag.
        :param config_repl: replication configuration block.
        """
        orphans: Set[ReplicationConfig] = set()
        notify = False
        for repl in config_repl:
            namespace = self._utils.parse_namespace(config_repl[repl])
            remote_cfgs = self._config.get_all_configs(self.run_env, namespace)

            if remote_cfgs:
                for cfg in remote_cfgs:
                    if cfg.source not in list(config_repl.keys()) \
                            and cfg.type == REPL_TYPE_APP \
                            and not cfg.source.startswith(shared_ns) \
                            and not cfg.source.startswith(self.context.defaults.service_ns):
                        orphans.add(cfg)
                        notify = True

        for orphan in orphans:
            print(f"{self.c.fg_rd}Orphaned replication mapping detected: {self.c.rs}"
                  f" {self.c.fg_bl}{orphan.source} -> {orphan.destination}{self.c.rs}.")
        if notify:
            print(f"To cleanup the now orphaned replication configs, "
                  f"delete the destination, THEN the source with the `figgy config delete` command")

    def _sync_replication(self, config_repl: Dict, expected_destinations: Set, namespace: str):
        """
        Calls sync_repl_configs which adds/removes repl configs. Then searches for orphaned configurations and notifies
        the user of detected orphaned configurations.
        Args:
            config_repl: Dict of KV Pairs for a repl config. Source -> Dest
            expected_destinations: expected replication destinations, as defined in merge key sources,
             or shared_figs
            namespace: Namespace to sync replication configs to. E.g. /app/demo-time/
        """

        print(f"{self.c.fg_gr}Validating replication for all parameters.{self.c.rs}")

        self._sync_repl_configs(config_repl, namespace=namespace)
        print(f"\n{self.c.fg_gr}Checking for orphaned replication configurations.{self.c.rs}")
        remote_cfgs = self._config.get_all_configs(self.run_env, namespace)
        notify = True
        if remote_cfgs:
            for cfg in remote_cfgs:
                if cfg.source not in list(config_repl.keys()) \
                        and cfg.destination not in list(config_repl.values()) \
                        and cfg.destination not in expected_destinations \
                        and (isinstance(cfg.source, list)
                             or cfg.source.startswith(shared_ns) or cfg.source.startswith(
                            self.context.defaults.service_ns)):
                    print(f"{self.c.fg_rd}Orphaned replication mapping detected: {self.c.rs}"
                          f" {self.c.fg_bl}{cfg.source} -> {cfg.destination}{self.c.rs}.")
                    notify = False
        if notify:
            print(f"{self.c.fg_bl}No orphaned replication configs found for: "
                  f"{self.c.rs}{self.c.fg_gr}{namespace}{self.c.rs}")
        else:
            print(f"{self.c.fg_bl}{CLEANUP_REPLICA_ORPHANS}{self.c.rs}")

    def _validate_merge_keys(self, destination: str, sources: Union[List, str], namespace: str) -> bool:
        """
        Validates merge key sources & destinations
        Args:
            destination: str -> Destination of merge key replication
            sources: List or Str -> Source(e) of this merge key
            namespace: application namespace
        """
        if not destination.startswith(namespace):
            print(f"{self.c.fg_rd}Merge config: {self.c.rs}{self.c.fg_bl}{destination}{self.c.rs}{self.c.fg_rd} has a "
                  f"destination that is not in your service namespace: "
                  f"{self.c.rs}{self.c.fg_bl}{namespace}{self.c.rs}{self.c.fg_rd}. This is invalid.{self.c.rs}")
            self.errors_detected = True
            return False

        if isinstance(sources, list):
            for item in sources:
                if item.startswith(MERGE_KEY_PREFIX):
                    self._utils.validate(item.replace(MERGE_KEY_PREFIX, "").startswith(namespace),
                                         f"Source: {item} in merge config must begin with your namespace: {namespace}.")
                    self.errors_detected = True
                    return False
        else:
            self._utils.validate(sources.startswith(namespace),
                                 f"Source {sources} in merge config must begin with your namespace: {namespace}")
            self.errors_detected = True
            return False

        return True

    def _sync_merge_keys(self, config_merge: Dict, namespace: str) -> None:
        """
            Pushes merge key configs into replication config table.
        Args:
            config_merge: Dict of merge_parameters parsed from figcli.json file
            namespace: namespace for app
        """
        print(f"{self.c.fg_gr}Validating replication for all merge keys.{self.c.rs}")
        for key in config_merge:
            self._validate_merge_keys(key, config_merge[key], namespace)

            config = self._config.get_config_repl(key, self.run_env)
            if not config or (config.source != config_merge[key]):
                try:
                    repl_config = ReplicationConfig(key, self.run_env, namespace,
                                                    config_merge[key], ReplicationType(REPL_TYPE_MERGE))
                    self._config.put_config_repl(repl_config)
                except ClientError:
                    self._utils.validate(False, f"Error detected when attempting to store replication config for {key}")
                    self._errors_detected = True
            else:
                print(f"Merge key replication config validated: {key}")

    def _validate_expected_names(self, all_names: Set, repl_conf: Dict, merge_conf: Dict):
        print(f"{self.c.fg_gr}Validating shared keys exist.{self.c.rs}")
        print_resolution_message = False
        merged_confs = {**repl_conf, **merge_conf}
        for name in all_names:
            if self._ssm.get_parameter_encrypted(name) is None:
                awaiting_repl = False
                for cnf in merged_confs:
                    if name == cnf or name in list(repl_conf.values()):
                        print(f"{self.c.fg_bl}Config value {name} is a destination for replication, but doesn't exist "
                              f"yet. If you commit now your build could fail. This will auto-resolve itself if all of "
                              f"its dependencies exist.{self.c.rs}")
                        awaiting_repl = True
                        break

                if not awaiting_repl:
                    print(f"Config value of {self.c.fg_rd}{name}{self.c.rs} does not exist and is expected based on"
                          f" your defined configuration.")
                    print_resolution_message = True
                    self._errors_detected = True

        if print_resolution_message:
            print(f"\n\n{self.c.fg_rd}{SHARED_NAME_RESOLUTION_MESSAGE}{self.c.rs}")

    def _can_replicate_from(self, source: str):
        try:
            if self._ssm.get_parameter_encrypted(source) is not None:
                return True
            else:
                print(f"{self.c.fg_yl}Replication source: {source} is missing from ParameterStore. "
                      f"It must be added before config replication can be configured.{self.c.rs}\n")
                self._input_config_values({source})
                return True
        except ClientError as e:
            denied = "AccessDeniedException" == e.response['Error']['Code']
            if denied and "AWSKMS; Status Code: 400;" in e.response['Error']['Message']:
                print(f"{self.c.fg_rd}You do not have access to decrypt the value of Name: {source}{self.c.rs}")
            elif denied:
                print(f"{self.c.fg_rd}You do not have access to Parameter: {source}{self.c.rs}")
            else:
                raise
        return False

    def _validate_replication_config(self, config_repl: Dict, app_conf: bool = True):
        """
        Validates replication config blocks are valid / legal. Prevents people from setting up replication from
        disallowed namespaces, etc. Exits with error if invalid config is discovered.

        Args:
            config_repl: Dict of KV Pairs for a repl config. Source -> Dest
            app_conf: bool: T/F - True if this is an application config block in an application config (figgy.json).
                    False if other, which for now is only repl-configs for data teams.
        """
        for key in config_repl:
            if app_conf:
                self._utils.validate(re.match(f'^/shared/.*$|^{self.context.defaults.service_ns}/.*$', key) is not None,
                                     f"The SOURCE of your replication configs must begin with `/shared/` or "
                                     f"`{self.context.defaults.service_ns}/`. "
                                     f"{key} is non compliant.")

            self._utils.validate(re.match(f'^{self.context.defaults.service_ns}/.*$', config_repl[key]) is not None,
                                 f"The DESTINATION of your replication configs must always begin with "
                                 f"`{self.context.defaults.service_ns}/`")

    def _find_missing_shared_figs(self, namespace: str, config_repl: Dict, shared_names: set, merge_conf: Dict):
        """
            Notifies the user if there is a parameter that has been shared into their namespace by an outside party
            but they have not added it to the `shared_figs` block of their figgy.json
        """
        all_repl_cfgs = self._config.get_all_configs(self.run_env, namespace)
        for cfg in all_repl_cfgs:
            in_merge_conf = self._in_merge_value(cfg.destination, merge_conf)

            if cfg.destination not in shared_names and cfg.type == REPL_TYPE_APP \
                    and cfg.destination not in config_repl.values() and not in_merge_conf:
                print(f"It appears that {self.c.fg_bl}{cfg.user}{self.c.rs} shared "
                      f"{self.c.fg_bl}{cfg.source}{self.c.rs} to {self.c.fg_bl}{cfg.destination}{self.c.rs} "
                      f"and you have not added {self.c.fg_bl}{cfg.destination}{self.c.rs} to the "
                      f"{self.c.fg_bl}{SHARED_KEY}{self.c.rs} section of your figgy.json. This is also not "
                      f"referenced in any defined merge parameter. Please add "
                      f"{self.c.fg_bl}{cfg.destination}{self.c.rs} to your figgy.json, or delete this parameter "
                      f"and the replication config with the cleanup command.")

    def _in_merge_value(self, dest: str, merge_conf: Dict):
        for key in merge_conf:
            value = merge_conf[key]
            # 'value' can be a list or a str, but the way 'in' operates, this works either way. #dynamic programming
            for suffix in merge_suffixes:
                if f"${'{'}{dest}{suffix}{'}'}" in value:
                    return True

        return False

    def run_ci_sync(self) -> None:
        """
            Orchestrates a standard `sync` command WITHOUT The `--replication-only` flag set.
        """
        # Validate & parse figgy.json
        config = self._utils.get_ci_config(self._config_path)
        shared_names = set(self._utils.get_config_key_safe(SHARED_KEY, config, default=[]))
        repl_conf = self._utils.get_config_key_safe(REPLICATION_KEY, config, default={})
        repl_from_conf = self._utils.get_config_key_safe(REPL_FROM_KEY, config, default={})
        merge_conf = self._utils.get_config_key_safe(MERGE_KEY, config, default={})
        config_keys = set(self._utils.get_config_key_safe(CONFIG_KEY, config, default=[]))
        namespace = self._utils.get_namespace(config)
        merge_keys = set(merge_conf.keys())
        all_keys = KeyUtils.find_all_expected_names(config_keys, shared_names, merge_conf, repl_conf,
                                                    repl_from_conf, namespace)

        repl_conf = KeyUtils.merge_repl_and_repl_from_blocks(repl_conf, repl_from_conf, namespace)
        # Add missing config values
        print()
        print(f"{self.c.fg_gr}Validating all configuration keys exist in ParameterStore.{self.c.rs}")
        self._input_config_values(config_keys)

        # Sync keys between PS / Local config
        print()
        self._sync_keys(namespace, all_keys)

        print()

        self._find_missing_shared_figs(namespace, repl_conf, shared_names, merge_conf)

        # Disabling requirement (for now) of replication to be in /replicated path
        # print()
        self._validate_replication_config(repl_conf, app_conf=True)

        print()
        # sync replication config
        all_shared_keys = shared_names | set(merge_conf.keys())
        self._sync_replication(repl_conf, all_shared_keys, namespace)

        print()
        self._sync_merge_keys(merge_conf, namespace)

        print()
        # validate expected keys exist
        self._validate_expected_names(all_keys, repl_conf, merge_conf)

    def run_repl_sync(self) -> None:
        """
        Orchestrates sync when the user passes in the `--replication-only` flag.
        """
        repl_conf = self._utils.get_repl_config(self._config_path)
        self._validate_replication_config(repl_conf, app_conf=False)
        self._sync_repl_configs(repl_conf)
        self._notify_of_data_repl_orphans(repl_conf)

    @VersionTracker.notify_user
    @AnonymousUsageTracker.track_command_usage
    def execute(self):
        print()
        if self._replication_only:
            self.run_repl_sync()
        else:
            self.run_ci_sync()

        if self._errors_detected:
            print(f"\r\n{self.c.fg_rd}Sync failed. Please address the outputted errors.{self.c.rs}")
        else:
            print(f"\r\n{self.c.fg_gr}Sync completed with no errors!{self.c.rs}")
