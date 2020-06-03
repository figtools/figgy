from figgy.commands.help_context import HelpContext
from figgy.commands.types.help import HelpCommand
from figgy.config import *
from figgy.svcs.observability.anonymous_usage_tracker import AnonymousUsageTracker
from figgy.svcs.observability.version_tracker import VersionTracker


class Version(HelpCommand):
    """
    Drives the --version command
    """

    def __init__(self, help_context: HelpContext):
        super().__init__(version, help_context.defaults.colors_enabled, help_context)
        self.tracker = VersionTracker(self.context.defaults)

    def version(self):
        self.tracker.check_version(self.c)

    @AnonymousUsageTracker.track_command_usage
    def execute(self):
        self.version()
