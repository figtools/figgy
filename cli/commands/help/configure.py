import json
import os
import base64
import xml.etree.ElementTree as ET
import re
import sys
import jsonpickle
from typing import Dict, List

from commands.types.help import HelpCommand
from config import *
from abc import ABC
from commands.help_context import HelpContext
from models.assumable_role import AssumableRole
from models.defaults import CLIDefaults
from models.role import Role
from models.run_env import RunEnv
from input.input import Input
from svcs.cache_manager import CacheManager
from svcs.sso.session_manager import SessionManager
from utils.secrets_manager import SecretsManager
from utils.utils import Utils
from tabulate import tabulate

class Configure(HelpCommand, ABC):
    """
    Drives the --configure command
    """

    def __init__(self, help_context: HelpContext, session_manager: SessionManager):
        super().__init__(configure, False, help_context)
        self._session_mgr = session_manager
        self._cache_mgr = CacheManager(DEFAULTS_FILE_CACHE_KEY)

    def configure(self):
        """
        Orchestrates the --configure option. Writes selections to a defaults file in user's home dir.

        This default files stores the following information:

        user: User Name for SSO integrations
        role: The user's preferred default role if --role is not specified
        env: The user's preferred eefault environment if --env is not specified
        valid_roles: A list of roles the user has access to based on the returned SAML assertion from the SSO provider
        valid_envs: A list of environments the user has access to based on the returned SAML assertion
        assumable_roles: Maintains a mapping of accountId -> environment name -> role name so the we can authenticate
                         the user with the appropriate AWS accounts based on their returned SAML assertion.
        """
        colors: bool = Input.select_enable_colors()
        self.c = Color(colors_enabled=colors)
        user: str = Input.get_okta_user()
        password: str = Input.get_okta_password()
        temp_env: RunEnv = RunEnv("unset")
        temp_role = Role("unset")

        defaults: CLIDefaults = CLIDefaults(role=temp_role, run_env=temp_env, user=user, colors_enabled=colors)
        SecretsManager.set_password(user, password)

        # Get assertion and parse out account -> role -> run_env mappings.
        assumable_roles: List[AssumableRole] = self._session_mgr.get_assumable_roles()

        print(f"\n{self.c.fg_bl}The following roles were detected for user: {user} - if something is missing, "
              f"contact your system administrator.{self.c.rs}\n")

        if assumable_roles:
            print(tabulate(
                    [x.tabulate_data() for x in assumable_roles],
                    headers=assumable_roles.pop().tabulate_header(),
                    tablefmt="grid",
                    numalign="center",
                    stralign="left",
                ))

        valid_envs = list(set([x.run_env.env for x in assumable_roles]))
        valid_roles = list(set([x.role.role for x in assumable_roles]))
        role: Role = Input.select_role(valid_roles=valid_roles)
        run_env: RunEnv = Input.select_default_account(valid_envs=valid_envs)
        defaults.role = role
        defaults.run_env = run_env
        defaults.valid_envs = valid_envs
        defaults.valid_roles = valid_roles
        defaults.assumable_roles = assumable_roles
        self._cache_mgr.write(DEFAULTS_FILE_CACHE_KEY, defaults)

    def execute(self):
        self.configure()
