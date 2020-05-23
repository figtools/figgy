from commands.help_context import HelpContext
from commands.types.help import HelpCommand
from config import *
from svcs.observability.usage_tracker import UsageTracker


class Version(HelpCommand):
    """
    Drives the --version command
    """

    def __init__(self, help_context: HelpContext):
        super().__init__(version, False, help_context)

    @staticmethod
    def version():
        print(f"Version: {VERSION}")

    @UsageTracker.track_command_usage
    def execute(self):
        self.version()
