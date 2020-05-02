from abc import ABC

from commands.help_context import HelpContext
from commands.types.command import Command
from commands.types.help import HelpCommand
from config import *


class Version(HelpCommand):
    """
    Drives the --version command
    """

    def __init__(self, help_context: HelpContext):
        super().__init__(version, False, help_context)

    @staticmethod
    def version():
        print(f"Version: {VERSION}")

    def execute(self):
        self.version()
