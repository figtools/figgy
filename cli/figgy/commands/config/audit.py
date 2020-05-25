from commands.config_context import ConfigContext
from commands.types.config import ConfigCommand
from data.dao.config import ConfigDao
from data.dao.ssm import SsmDao
from svcs.observability.usage_tracker import UsageTracker
from svcs.observability.version_tracker import VersionTracker
from utils.utils import *


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
    @UsageTracker.track_command_usage
    def execute(self):
        self._audit()
