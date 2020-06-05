import requests
from abc import ABC
import re
from typing import List
from figgy.commands.help_context import HelpContext
from figgy.commands.types.help import HelpCommand
from figgy.config import *
from figgy.input.input import Input, Utils
from figgy.models.assumable_role import AssumableRole
from figgy.models.defaults.defaults import CLIDefaults
from figgy.models.defaults.provider import Provider
from figgy.models.role import Role
from figgy.svcs.cache_manager import CacheManager
from figgy.svcs.config_manager import ConfigManager
from figgy.svcs.observability.anonymous_usage_tracker import AnonymousUsageTracker
from figgy.svcs.observability.version_tracker import VersionTracker
from figgy.svcs.setup import FiggySetup
from figgy.svcs.sso.provider.provider_factory import SessionProviderFactory
from figgy.models.sandbox.login_response import SandboxLoginResponse

from figgy.utils.awscli import AWSCLIUtils


class Login(HelpCommand, ABC):
    """
    Log the user into every possible environment they have access to. Sessions are cached.
    This improves figgy performance throughout the day.
    """

    def __init__(self, help_context: HelpContext, figgy_setup: FiggySetup):
        super().__init__(login, Utils.not_windows(), help_context)
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

    def login_sandbox(self):
        print(f"{self.c.fg_bl}Logging you into the Figgy Sandbox environment.{self.c.rs}")
        user = Input.input("Please input a user name: ")

        role = Input.select("Please select a role to impersonate: ", valid_options=SANDBOX_ROLES)
        colors = Input.select_enable_colors()
        params = {'role': role, 'user': user}
        result = requests.get(GET_SANBOX_CREDS_URL, params=params)

        if result.status_code != 200:
            self._utils.error_exit("Unable to get temporary credentials from the Figgy sandbox. If this problem "
                                   f"persists please notify us on our GITHUB: {FIGGY_GITHUB}")

        data = result.json()
        response = SandboxLoginResponse(**data)
        AWSCLIUtils.write_credentials(access_key=response.AWS_ACCESS_KEY_ID, secret_key=response.AWS_SECRET_ACCESS_KEY,
                                      token=response.AWS_SESSION_TOKEN, region=FIGGY_SANDBOX_REGION,
                                      profile_name=FIGGY_SANDBOX_PROFILE, color=self.c)

        defaults = CLIDefaults.sandbox(user=user, role=role, colors=colors)
        self._setup.save_defaults(defaults)

        config_mgr = ConfigManager.figgy()
        config_mgr.set(Config.Section.Bastion.PROFILE, FIGGY_SANDBOX_PROFILE)
        defaults = self._setup.configure_roles(current_defaults=defaults, role=Role(role))
        self._setup.save_defaults(defaults)

        print(f"\n{self.c.fg_gr}Login successful. Your sandbox session will last for{self.c.rs} "
              f"{self.c.fg_bl}1 hour.{self.c.rs}")

        print(f"\nIf your session expires, feel free to rerun `{CLI_NAME} login sandbox` to get another sandbox session. "
              f"\nAll previous figgy sessions have been disabled, you'll need to run {CLI_NAME} "
              f"--configure to leave the sandbox.")


    @VersionTracker.notify_user
    @AnonymousUsageTracker.track_command_usage
    def execute(self):
        if self.context.command == login:
            self.login()
        elif self.context.command == sandbox:
            self.login_sandbox()
