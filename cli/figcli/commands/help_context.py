from typing import Optional, List, Set

from figcli.commands.command_context import CommandContext
from figcli.models.defaults.defaults import CLIDefaults
from figcli.models.run_env import RunEnv


class HelpContext(CommandContext):
    """
    Contextual information for HelpCommands, including _what_ command resources were passed in. Help commands
    often don't have standard "resource" or "command" blocks, instead they may ONLY have --optional parameters
    """
    def __init__(self, resource: Optional[frozenset], command: Optional[frozenset],
                 options: Optional[Set[frozenset]], run_env: Optional[RunEnv], defaults: Optional[CLIDefaults]):
        super().__init__(run_env, resource, defaults=defaults)

        self.resource = resource
        self.command = command
        self.options = options
