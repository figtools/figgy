from typing import Optional

from figgy.config import *
from abc import ABC, abstractmethod
from figgy.commands.config_context import ConfigContext
from figgy.commands.command_context import CommandContext
from figgy.commands.types.command import Command
from figgy.models.defaults.defaults import CLIDefaults


class ConfigCommand(Command, ABC):
    """
    Config command class from which all other config command classes inherit.
    """

    def __init__(self, command_type: frozenset, colors_enabled: bool, context: ConfigContext):
        super().__init__(command_type, colors_enabled, context)
        self.role = context.role
