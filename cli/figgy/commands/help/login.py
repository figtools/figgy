from abc import ABC
from typing import List
from commands.help_context import HelpContext
from commands.types.help import HelpCommand
from config import *
from input.input import Input, Utils
from models.assumable_role import AssumableRole
from models.defaults.defaults import CLIDefaults
from models.defaults.provider import Provider
from svcs.observability.usage_tracker import UsageTracker
from svcs.observability.version_tracker import VersionTracker
from svcs.setup import FiggySetup
from svcs.sso.provider.provider_factory import SessionProviderFactory
from concurrent.futures import ThreadPoolExecutor, as_completed


class Login(HelpCommand, ABC):
    """
    Log the user into every possible environment they have access to. Sessions are cached.
    This improves figgy performance throughout the day.
    """

    def __init__(self, help_context: HelpContext, figgy_setup: FiggySetup):
        super().__init__(configure, False, help_context)
        self._setup = figgy_setup
        self._defaults: CLIDefaults = figgy_setup.get_defaults()
        self._utils = Utils(self._defaults.colors_enabled)

    def login(self):
        self._utils.validate(self._defaults.provider.name in Provider.names(),
                             f"You cannot login until you've configured Figgy. Please run `{CLI_NAME}` --configure")
        provider = SessionProviderFactory(self._defaults).instance()
        assumable_roles: List[AssumableRole] = provider.get_assumable_roles()
        print(f"{self.c.bl}Found {len(assumable_roles)} possible logins. Logging in...{self.c.rs}")

        for role in assumable_roles:
            print(f"Login successful for {role.role} in environment: {role.run_env}")
            provider.get_session_and_role(role, False)

        print(f"{self.c.gr}Login successful. All sessions are cached.{self.c.rs}")

    @VersionTracker.notify_user
    @UsageTracker.track_command_usage
    def execute(self):
        self.login()
