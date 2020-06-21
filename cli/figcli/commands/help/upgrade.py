from figcli.commands.help_context import HelpContext
from figcli.commands.types.help import HelpCommand
from figcli.config import *
from figcli.svcs.observability.anonymous_usage_tracker import AnonymousUsageTracker
from figcli.svcs.observability.version_tracker import VersionTracker
from figcli.svcs.upgrade_manager import UpgradeManager
from figcli.utils.utils import Utils


class Upgrade(HelpCommand):
    """
    Drives the --version command
    """

    def __init__(self, help_context: HelpContext):
        super().__init__(version, help_context.defaults.colors_enabled, help_context)
        self.tracker = VersionTracker(self.context.defaults)
        self.upgrade_mgr = UpgradeManager(help_context.defaults.colors_enabled)
        self._utils = Utils(colors_enabled=help_context.defaults.colors_enabled)

    def upgrade(self):
        current_version = self.tracker.get_version()
        if self.tracker.upgrade_available(current_version.version, VERSION):
            print(f'{self.c.fg_yl}------------------------------------------{self.c.rs}')
            print(f' New version: {self.c.rs}{self.c.fg_gr}{current_version.version}{self.c.rs} is more '
                  f'recent than your version: {self.c.fg_gr}{VERSION}{self.c.rs}')
            print(f'{self.c.fg_yl}------------------------------------------{self.c.rs}')

            if self._utils.is_mac():
                print(f"\nMacOS auto-upgrade is supported. Performing auto-upgrade.")
                self.upgrade_mgr.install_mac_onedir()



        print(f"{self.c.fg_gr}Installation successful! Exiting. Rerun `{CLI_NAME}` "
              f"to use the latest version!{self.c.rs}")

    @AnonymousUsageTracker.track_command_usage
    def execute(self):
        self.upgrade()
