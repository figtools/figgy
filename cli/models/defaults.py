from models.role import Role
from models.run_env import RunEnv
from config import *
from typing import Dict


class CLIDefaults:
    """
    Defaults are parsed from the ~/.figgy/devops/defaults file and then hydrate this object
    """

    def __init__(self, role: Role, colors_enabled: bool, okta_user: str, env: RunEnv):
        self.role = role  # type: Role
        self.colors_enabled = colors_enabled  # type: bool
        self.run_env = env  # type: RunEnv
        self.okta_user = okta_user

    def __str__(self):
        return f"Role: {self.role}\nColors Enabled: {self.colors_enabled}\nOkta User: {self.okta_user}\n" \
            f"Default Environment: {self.run_env}"

    @staticmethod
    def from_dict(config: Dict):
        role: Role = Role(config.get(DEFAULTS_ROLE_KEY))
        colors_enabled = config.get(COLORS_ENABLED_KEY)
        user_name = config.get(OKTA_USER_KEY)
        env = RunEnv(config.get(DEFAULT_ENV_KEY, dev))  # Default to dev if missing.

        return CLIDefaults(role, colors_enabled, user_name, env)
