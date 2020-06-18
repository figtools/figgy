from typing import Union

from figcli.commands.config_context import ConfigContext
from figcli.commands.help_context import HelpContext
from figcli.config import *
from figcli.config.style.terminal_factory import TerminalFactory
from figcli.utils.utils import Utils
from abc import ABC, abstractmethod
from figcli.commands.command_context import CommandContext


class Command(ABC):
    """
    Root command class from which all other command classes inherit.
    """

    def __init__(self, command_type: frozenset, colors_enabled: bool,
                 context: Union[CommandContext, HelpContext, ConfigContext]):
        self.type = command_type
        self.run_env = context.run_env
        self.c = TerminalFactory(colors_enabled).instance().get_colors()
        self.command_printable = list(self.type)[0]
        self.context = context
        self.example = f"{self.c.fg_bl}{CLI_NAME} {Utils.get_first(context.resource)} {self.command_printable} " \
                       f"--env dev{self.c.rs}"

    @abstractmethod
    def execute(self):
        pass

    def print_help_text(self):
        """
        This help text is printed when users pass in the --info option
        :param command: one of the define commands in config.py
        """

        optional_params = frozenset(filter(lambda x: not arg_options[self.context.resource][self.type][x][required],
                                           arg_options[self.context.resource][self.type].keys()))

        required_params = frozenset(filter(lambda x: arg_options[self.context.resource][self.type][x][required],
                                           arg_options[self.context.resource][self.type].keys()))

        print(f"Command: {self.c.fg_bl}{self.command_printable}{self.c.rs}")
        if len(required_params) > 0:
            print(f"Required parameters: {self.c.fg_bl}{CollectionUtils.printable_set(required_params)}{self.c.rs}")

        if len(optional_params) > 0:
            print(f"Optional parameters: {self.c.fg_bl}{CollectionUtils.printable_set(optional_params)}{self.c.rs}")

        print(f"Example: {self.example}")
        print(f"\n\n{HELP_TEXT_MAP[self.type]}\n")
