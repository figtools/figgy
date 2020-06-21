from abc import ABC
import sys
from typing import List, Dict

from tabulate import tabulate

from figcli.commands.help_context import HelpContext
from figcli.commands.types.help import HelpCommand
from figcli.config import *
from figcli.config.style.terminal_factory import TerminalFactory
from figcli.utils.utils import Utils
from figcli.input.input import Input
from figcli.models.assumable_role import AssumableRole
from figcli.models.defaults.defaults import CLIDefaults
from figcli.models.role import Role
from figcli.models.run_env import RunEnv
from figcli.svcs.setup import FiggySetup
from figcli.svcs.auth.provider.provider_factory import SessionProviderFactory
from figcli.svcs.auth.provider.session_provider import SessionProvider


class Configure(HelpCommand, ABC):
    """
    Drives the --configure command
    """

    def __init__(self, help_context: HelpContext, figgy_setup: FiggySetup):
        super().__init__(configure, False, help_context)
        self._setup = figgy_setup

    def configure(self) -> CLIDefaults:
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
        Utils.wipe_vaults() or Utils.wipe_defaults() or Utils.wipe_config_cache()
        defaults: CLIDefaults = self._setup.get_defaults()
        defaults = self._setup.configure_auth(defaults)
        defaults = self._setup.configure_extras(defaults)
        self._setup.save_defaults(defaults)
        self.c = TerminalFactory(Utils.is_mac()).instance().get_colors()

        defaults = self._setup.configure_roles(current_defaults=defaults)
        defaults = self._setup.configure_preferences(defaults)
        defaults = self._setup.configure_figgy_defaults(defaults)
        self._setup.save_defaults(defaults)
        print(f"\n{self.c.fg_gr}Setup successful! Enjoy figgy!{self.c.rs}")
        return defaults

    def execute(self):
        self.configure()
