from abc import ABC
from typing import List, Dict

from tabulate import tabulate

from commands.help_context import HelpContext
from commands.types.help import HelpCommand
from config import *
from utils.utils import Utils
from input.input import Input
from models.assumable_role import AssumableRole
from models.defaults.defaults import CLIDefaults
from models.role import Role
from models.run_env import RunEnv
from svcs.setup import FiggySetup
from svcs.sso.provider.provider_factory import SessionProviderFactory
from svcs.sso.provider.session_provider import SessionProvider


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
        defaults: CLIDefaults = CLIDefaults.unconfigured()
        defaults = self._setup.configure_auth(defaults)
        self._setup.save_defaults(defaults)
        self.c = Color(colors_enabled=Utils.is_mac())

        provider_factory: SessionProviderFactory = SessionProviderFactory(defaults)
        session_provider: SessionProvider = provider_factory.instance()
        session_provider.cleanup_session_cache()
        # Get assertion and parse out account -> role -> run_env mappings.
        assumable_roles: List[AssumableRole] = session_provider.get_assumable_roles()
        print(f"\n{self.c.fg_bl}The following roles were detected for user: {defaults.user} - if something is missing, "
              f"contact your system administrator.{self.c.rs}\n")

        if assumable_roles:
            self.print_role_table(assumable_roles)

        valid_envs = list(set([x.run_env.env for x in assumable_roles]))
        valid_roles = list(set([x.role.role for x in assumable_roles]))
        role: Role = Input.select_role(valid_roles=valid_roles)
        print("\n")
        run_env: RunEnv = Input.select_default_account(valid_envs=valid_envs)
        print("\n")
        defaults.role = role
        defaults.run_env = run_env
        defaults.valid_envs = valid_envs
        defaults.valid_roles = valid_roles
        defaults.assumable_roles = assumable_roles
        defaults = self._setup.configure_preferences(defaults)
        self._setup.save_defaults(defaults)
        print(f"\n{self.c.fg_gr}Setup successful! Enjoy figgy!{self.c.rs}")
        return defaults

    @staticmethod
    def print_role_table(roles: List[AssumableRole]):
        printable_roles: Dict[int: Dict] = {}
        for role in roles:
            item = printable_roles.get(role.account_id, {})
            item['env'] = role.run_env.env
            item['roles'] = item.get('roles', []) + [role.role.role]
            printable_roles[role.account_id] = item

        print(tabulate(
            [
                [
                    account_id,
                    printable_roles[account_id]['env'],
                    ', '.join(printable_roles[account_id]['roles'])
                ]
                for account_id in printable_roles.keys()
            ],
            headers=['AccountId', 'Environment', 'Roles'],
            tablefmt="grid",
            numalign="center",
            stralign="left",
        ))

    def execute(self):
        self.configure()
