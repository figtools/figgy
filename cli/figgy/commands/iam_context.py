from typing import Optional

from models.defaults.defaults import CLIDefaults
from models.run_env import RunEnv
from models.role import Role
from commands.command_context import CommandContext


class IAMContext(CommandContext):
    """
    All `iam` resource commands require this context for general use. Config commands operate differently based on
    Role and RunEnv
    """
    def __init__(self, run_env: RunEnv, role: Role, colors_enabled: bool, resource: frozenset,
                 defaults: Optional[CLIDefaults]):
        super().__init__(run_env, resource, defaults=defaults)
        self.role: Role = role
        self.colors_enabled = colors_enabled
