from abc import ABC

from figcli.commands.command_context import CommandContext
from figcli.commands.iam_context import IAMContext
from figcli.commands.types.command import Command


class IAMCommand(Command, ABC):
    """
    Config command class from which all other config command classes inherit.
    """

    def __init__(self, command_type: frozenset, context: IAMContext):
        super().__init__(command_type, context.colors_enabled, CommandContext(context.run_env, context.resource,
                                                                              context.defaults))
        self.role = context.role
