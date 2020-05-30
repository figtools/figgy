from commands.factory import Factory
from commands.help.login import Login
from commands.help.version import Version
from commands.help_context import HelpContext
from commands.help.configure import Configure
from config import *
from svcs.setup import FiggySetup
from svcs.sso.session_manager import SessionManager
from utils.utils import Utils, CollectionUtils


class HelpFactory(Factory):
    def __init__(self, command: frozenset, context: HelpContext):
        self._command = command
        self._context = context
        self._options = context.options
        self._utils = Utils(False)
        self._setup: FiggySetup = FiggySetup()

    def instance(self):
        return self.get(self._command)

    def get(self, command: frozenset):
        if configure in self._options:
            return Configure(self._context, self._setup)
        elif version in self._options:
            return Version(self._context)
        elif command == login or command == sandbox:
            return Login(self._context, self._setup)
        else:
            self._utils.error_exit(f"{Utils.get_first(command)} is not a valid command. You must select from: "
                                   f"[{CollectionUtils.printable_set(help_commands)}]. Try using --help for more info.")
