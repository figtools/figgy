from figcli.commands.help_context import HelpContext
from figcli.commands.types.help import HelpCommand
from figcli.config import *
from figcli.input import Input
from figcli.svcs.observability.anonymous_usage_tracker import AnonymousUsageTracker
from figcli.svcs.observability.version_tracker import VersionTracker, FiggyVersionDetails
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
        self._utils.error_exit("This command has been deprecated and disabled. Please use the standard upgrade process"
                               "through `homebrew` or `pip`.")
        latest_version: FiggyVersionDetails = self.tracker.get_version()

        if latest_version.version == VERSION:
            print(f'{self.c.fg_bl}You are currently using the latest version of {CLI_NAME}: {self.c.rs}'
                  f'{self.c.fg_gr}{VERSION}{self.c.rs}')

        elif self.tracker.upgrade_available(VERSION, latest_version.version):
            print(f'{self.c.fg_yl}------------------------------------------{self.c.rs}')
            print(f' New version: {self.c.rs}{self.c.fg_gr}{latest_version.version}{self.c.rs} is more '
                  f'recent than your version: {self.c.fg_gr}{VERSION}{self.c.rs}')
            print(f'{self.c.fg_yl}------------------------------------------{self.c.rs}')

            if self._utils.is_mac():
                print(f"\nMacOS auto-upgrade is supported. Performing auto-upgrade.")
                self.install_mac(latest_version)
            print(f"{self.c.fg_gr}Installation successful! Exiting. Rerun `{CLI_NAME}` "
                  f"to use the latest version!{self.c.rs}")
        else:
            print(f'{self.c.fg_yl}------------------------------------------{self.c.rs}')
            print(f'Your version: {self.c.rs}{self.c.fg_gr}{latest_version.version}{self.c.rs} is more '
                  f'recent than the current recommended version of {CLI_NAME}: {self.c.fg_gr}{VERSION}{self.c.rs}')
            print(f'{self.c.fg_yl}------------------------------------------{self.c.rs}')

            if self._utils.is_mac():
                selection = Input.y_n_input(f'Would you like to revert to the current recommended version '
                                            f'of {CLI_NAME}?')
                if selection:
                    self.install_mac(latest_version)

    def install_mac(self, latest_version: FiggyVersionDetails):
        install_path = self.upgrade_mgr.get_install_path()
        self.upgrade_mgr.install_mac_onedir(install_path, latest_version.version)

    @AnonymousUsageTracker.track_command_usage
    def execute(self):
        self.upgrade()
