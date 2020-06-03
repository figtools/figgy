from figgy.commands.config_context import ConfigContext
from figgy.commands.types.config import ConfigCommand
from figgy.data.dao.config import ConfigDao
from figgy.data.dao.ssm import SsmDao
from figgy.svcs.observability.anonymous_usage_tracker import AnonymousUsageTracker
from figgy.svcs.observability.version_tracker import VersionTracker
from figgy.utils.utils import *


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
            ps_name = prompt(f"Please input a PS Name : ", completer=self._config_completer)
            if self._utils.is_valid_input(ps_name, 'Parameter Name', notify=True):
                audit_logs = self._config.get_audit_logs(ps_name)
                result_count = len(audit_logs)
                if result_count > 0:
                    print(f"\r\nFound {result_count} results.")
                else:
                    print(f"\r\nNo results found for {ps_name}")
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
