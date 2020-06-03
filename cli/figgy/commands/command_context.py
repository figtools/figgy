from typing import Optional

from figgy.models.defaults.defaults import CLIDefaults
from figgy.models.run_env import RunEnv


class CommandContext:
    """
    All commands, regardless of resource type, will need to know what RunEnvironment they are operating on. That is the
    purpose of this command context. Similar properties would be added here.
    """
    def __init__(self, run_env: RunEnv, resource: frozenset, defaults: Optional[CLIDefaults]):
        self.run_env = run_env  # type: RunEnv
        self.resource = resource
        self.defaults = defaults
