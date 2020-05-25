from commands.help_context import HelpContext
from commands.types.help import HelpCommand
from config import *
from svcs.observability.usage_tracker import UsageTracker
from svcs.observability.version_tracker import VersionTracker


class Version(HelpCommand):
    """
    Drives the --version command
    """

    def __init__(self, help_context: HelpContext):
        super().__init__(version, help_context.defaults.colors_enabled, help_context)
        self.tracker = VersionTracker(self.context.defaults)

    def version(self):
        self.tracker.check_version(self.c)

    @UsageTracker.track_command_usage
    def execute(self):
        self.version()
