from figcli.commands.config_context import ConfigContext
from figcli.commands.types.config import ConfigCommand
from figcli.config import *
from figcli.data.dao.config import ConfigDao
from figcli.data.dao.ssm import SsmDao
from figcli.extras.key_utils import KeyUtils
from figcli.svcs.observability.anonymous_usage_tracker import AnonymousUsageTracker
from figcli.svcs.observability.version_tracker import VersionTracker
from figcli.utils.utils import Utils


class Validate(ConfigCommand):

    def __init__(self, ssm_init: SsmDao, colors_enabled: bool, context: ConfigContext):
        super().__init__(validate, colors_enabled, context)
        self._ssm = ssm_init
        self._config_path = context.ci_config_path if context.ci_config_path else Utils.find_figgy_json()
        self._utils = Utils(colors_enabled)
        self._replication_only = context.replication_only
        self._errors_detected = False
        self.example = f"{self.c.fg_bl}{CLI_NAME} config {self.command_printable} " \
                       f"--env dev --config /path/to/config{self.c.rs}"
        self._FILE_PREFIX = "file://"

    def _validate(self):
        missing_key = False
        config = self._utils.get_ci_config(self._config_path)
        shared_names = set(self._utils.get_config_key_safe(SHARED_KEY, config, default=[]))
        repl_conf = self._utils.get_config_key_safe(REPLICATION_KEY, config, default={})
        repl_from_conf = self._utils.get_config_key_safe(REPL_FROM_KEY, config, default={})
        merge_conf = self._utils.get_config_key_safe(MERGE_KEY, config, default={})
        config_keys = set(self._utils.get_config_key_safe(CONFIG_KEY, config, default=[]))
        namespace = self._utils.get_namespace(config)
        all_names = KeyUtils.find_all_expected_names(config_keys, shared_names, merge_conf, repl_conf,
                                                     repl_from_conf, namespace)

        all_params = self._ssm.get_all_parameters([namespace])

        all_param_names = []
        for param in all_params:
            all_param_names.append(param['Name'])

        print()
        for name in all_names:
            if name not in all_param_names:
                print(f"Fig missing from {self.c.fg_yl}{self.run_env}{self.c.rs} environment"
                      f" Parameter Store: {self.c.fg_yl}{name}{self.c.rs}")
                missing_key = True
            else:
                print(f"Fig found in ParameterStore: {self.c.fg_bl}{name}{self.c.rs}.")

        if missing_key:
            print("\n\n")
            self._utils.error_exit(f"{MISSING_PS_NAME_MESSAGE}")
        else:
            print(f"{self.c.fg_gr}Success! All figs have been located in the {self.c.rs}{self.c.fg_bl}{self.run_env}"
                  f"{self.c.rs} ParameterStore!")

    @VersionTracker.notify_user
    @AnonymousUsageTracker.track_command_usage
    def execute(self):
        self._validate()
