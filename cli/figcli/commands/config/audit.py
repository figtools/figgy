from prompt_toolkit.completion import WordCompleter

from figcli.commands.config_context import ConfigContext
from figcli.commands.types.config import ConfigCommand
from figcli.data.dao.config import ConfigDao
from figcli.data.dao.ssm import SsmDao
from figcli.input import Input
from figcli.svcs.observability.anonymous_usage_tracker import AnonymousUsageTracker
from figcli.svcs.observability.version_tracker import VersionTracker
from figcli.utils.utils import *


class Audit(ConfigCommand):
    """
    Returns audit history for a queried PS Name
    """
    def __init__(self, ssm_init: SsmDao, config_init: ConfigDao, config_completer_init: WordCompleter,
                 colors_enabled: bool, config_context: ConfigContext):
        super().__init__(audit, colors_enabled, config_context)
        self._ssm = ssm_init
        self._config = config_init
        self._config_completer = config_completer_init
        self._utils = Utils(colors_enabled)

    def _audit(self):
        audit_more = True

        while audit_more:
            ps_name = Input.input(f"Please input a PS Name : ", completer=self._config_completer)
            audit_logs = self._config.get_audit_logs(ps_name)
            result_count = len(audit_logs)
            if result_count > 0:
                print(f"\nFound {self.c.fg_bl}{result_count}{self.c.rs} results.")
            else:
                print(f"\n{self.c.fg_yl}No results found for: {ps_name}{self.c.rs}")
            for log in audit_logs:
                print(log)

            to_continue = input(f"Audit another? (Y/n): ")
            to_continue = to_continue if to_continue != '' else 'y'
            audit_more = to_continue.lower() == "y"
            print()

    @VersionTracker.notify_user
    @AnonymousUsageTracker.track_command_usage
    def execute(self):
        self._audit()
