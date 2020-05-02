import json
import os

from typing import Dict

from commands.types.help import HelpCommand
from config import *
from abc import ABC
from commands.help_context import HelpContext
from commands.types.command import Command
from models.role import Role
from models.run_env import RunEnv
from input.input import Input
from utils.secrets_manager import SecretsManager


class Configure(HelpCommand, ABC):
    """
    Drives the --configure command
    """

    def __init__(self, help_context: HelpContext):
        super().__init__(configure, False, help_context)

    @staticmethod
    def configure():
        """
        Orchestrates the --configure option. Writes selections to a defaults file in user's home dir.
        """
        role: Role = Input.select_role()
        colors: bool = Input.select_enable_colors()
        user: str = Input.get_okta_user()
        password: str = Input.get_okta_password()
        env: RunEnv = Input.select_default_account()

        opts: Dict = {DEFAULTS_ROLE_KEY: role.role,
                      COLORS_ENABLED_KEY: colors, OKTA_USER_KEY: user,
                      DEFAULT_ENV_KEY: env.env}

        SecretsManager.set_password(user, password)

        os.makedirs(os.path.dirname(DEFAULTS_FILE_PATH), exist_ok=True)
        with open(DEFAULTS_FILE_PATH, "w") as cache:
            cache.write(json.dumps(opts))

        print(f"{CLI_NAME} successfully configured.")

    def execute(self):
        self.configure()
