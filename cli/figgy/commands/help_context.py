from typing import Optional, List, Set

from commands.command_context import CommandContext
from models.run_env import RunEnv


class HelpContext(CommandContext):
    """
    Contextual information for HelpCommands, including _what_ command resources were passed in. Help commands
    often don't have standard "resource" or "command" blocks, instead they may ONLY have --optional parameters
    """
    def __init__(self, resource: Optional[frozenset], command: Optional[frozenset],
                 options: Optional[Set[frozenset]], run_env: Optional[RunEnv]):
        super().__init__(run_env, resource)

        self.resource = resource
        self.command = command
        self.options = options
