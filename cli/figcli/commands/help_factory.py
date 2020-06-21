from figcli.commands.factory import Factory
from figcli.commands.help.login import Login
from figcli.commands.help.upgrade import Upgrade
from figcli.commands.help.version import Version
from figcli.commands.help_context import HelpContext
from figcli.commands.help.configure import Configure
from figcli.config import *
from figcli.svcs.setup import FiggySetup
from figcli.svcs.auth.session_manager import SessionManager
from figcli.utils.utils import Utils, CollectionUtils


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
        elif upgrade in self._options:
            return Upgrade(self._context)
        else:
            self._utils.error_exit(f"{Utils.get_first(command)} is not a valid command. You must select from: "
                                   f"[{CollectionUtils.printable_set(help_commands)}]. Try using --help for more info.")
