import argparse
import getpass
import logging
import os
import sys
import boto3

from json import JSONDecodeError
from typing import Optional, List
from figgy.config import *
from figgy.input.input import Input
from figgy.models.assumable_role import AssumableRole
from figgy.models.defaults.defaults import CLIDefaults
from figgy.models.role import Role
from figgy.models.run_env import RunEnv
from figgy.svcs.cache_manager import CacheManager
from figgy.svcs.observability.error_reporter import FiggyErrorReporter
from figgy.svcs.sso.provider.provider_factory import SessionProviderFactory
from figgy.svcs.sso.session_manager import SessionManager
from figgy.utils.utils import Utils

from figgy.commands.command_factory import CommandFactory
from figgy.commands.figgy_context import FiggyContext
from figgy.commands.types.command import Command

root_logger = logging.getLogger()
root_logger.setLevel(logging.CRITICAL)
root_logger.handlers = []
stdout_handler = logging.StreamHandler(sys.stdout)

log = logging.getLogger(__name__)


class FiggyCLI:
    @staticmethod
    def add_arg(com_parser, com_arg, cmd, rsc):
        com_parser.add_argument(f'--{Utils.get_first(com_arg)}', help=HELP_TEXT_MAP[com_arg],
                                action=arg_options[rsc][cmd][com_arg][action],
                                required=arg_options[rsc][cmd][com_arg][required])

    @staticmethod
    def parse_args():
        """
        Parses Figgy command line arguments and returns generic "args" object.
        """
        parser = argparse.ArgumentParser(description=RESOURCE_PARSER_DESC)
        parser.add_argument(f'--{Utils.get_first(configure)}', help=CONFIGURE_HELP_TEXT, action=store_true)
        parser.add_argument(f'--{Utils.get_first(prompt_com)}', help=PROMPT_HELP_TEXT, action=store_true)
        parser.add_argument(f'--{Utils.get_first(version)}', help=VERSION_HELP_TEXT, action=store_true)
        parser.add_argument(f'--{Utils.get_first(skip_upgrade)}', help=SKIP_UPGRADE_HELP_TEXT, action=store_true)

        resource_subparsers = parser.add_subparsers(title='resources', dest='resource', metavar='')

        for rsc in resource_map:
            cmd_parser = resource_subparsers.add_parser(Utils.get_first(rsc), help=HELP_TEXT_MAP[rsc])
            subparser = cmd_parser.add_subparsers(title=f'{Utils.get_first(rsc)} commands', dest='command', metavar='',
                                                  help=HELP_TEXT_MAP[rsc])

            for cmd in resource_map[rsc]:
                com_parser = subparser.add_parser(Utils.get_first(cmd), help=HELP_TEXT_MAP[cmd])
                for com_arg, val in arg_options[rsc][cmd].items():
                    FiggyCLI.add_arg(com_parser, com_arg, cmd, rsc)

        return parser.parse_args()

    @staticmethod
    def get_defaults(skip: bool = False) -> Optional[CLIDefaults]:
        """Lookup a user's defaults as configured by --configure option.
        :param skip - Boolean, if this is true, exit and return none.
        :return: hydrated CLIDefaults object of default values stored in cache file or None if no cache found
        """

        if skip:
            return CLIDefaults.unconfigured()

        cache_mgr = CacheManager(DEFAULTS_FILE_CACHE_KEY)
        try:
            last_write, defaults = cache_mgr.get(DEFAULTS_FILE_CACHE_KEY)

            if not defaults:
                Utils.stc_error_exit(f'{CLI_NAME} has not been configured. '
                                     f'Please run {CLI_NAME} --{Utils.get_first(configure)}')

            return defaults
        except JSONDecodeError:
            return None

    def get_profile(self, prompt: bool) -> str:
        """Returns the user's profile.

        Checks ENV variable, if not there, checks the config file (created via the --configure option), otherwise prompts
        the user

        Args:
            prompt: True/False - if True, users will always be prompted to input their profile

        :return: str: aws profile name
        """

        if BASTION_PROFILE_ENV_NAME in os.environ and not prompt:
            return os.environ.get(BASTION_PROFILE_ENV_NAME)
        else:
            defaults: CLIDefaults = self.get_defaults(self._is_setup_command)
            if defaults is not None and not prompt:
                return defaults.provider_config.profile
            else:
                return Input.select_aws_cli_profile()

    def get_role(self, prompt: bool, role_override: str = None) -> Role:
        """
        Returns a string of the user's selected role.

        Lookup the user's default role from the config file (created via the --configure option), an ENV variable, or
        instead prompt the user for the session.

        :param prompt: True/False - if True, users will always be prompted to input their role
        :param role_override: String representation of the role to get, regardless of defaults.
        :return: str: name of the selected role.
        """

        if role_override:
            print(f'Role override selected: {role_override}\n')
            return Role(role_override)

        defaults = self.get_defaults(self._is_setup_command)
        if defaults is not None and not prompt:
            return defaults.role
        else:
            #Todo this BROKE
            return Input.select_role()

    def get_colors_enabled(self) -> bool:
        """
        Defaults to true, unless user ran --configure and disabled colored output
        Returns: True/False

        """
        defaults = self.get_defaults(skip=self._is_setup_command)
        if defaults is not None:
            return defaults.colors_enabled
        else:
            return Utils.not_windows()

    def get_command(self) -> Command:
        """
        Maps the user's passed in text command to one of our defined 'command' objects we use in the code.
        Args:

        Returns: command object.
        """
        return self.get_command_factory().instance()

    def find_assumable_role(self, env: RunEnv, role: Role, skip: bool = False) -> AssumableRole:
        assumable_roles: List[AssumableRole] = self.get_defaults(skip=skip).assumable_roles
        matching_role = [ar for ar in assumable_roles if ar.role == role and ar.run_env == env]
        if matching_role:
            matching_role = matching_role.pop()
        else:
            matching_role = None

        return matching_role

    @staticmethod
    def is_setup_command(args):
        return Utils.is_set_true(configure, args) or Utils.command_set(sandbox, args)

    def __init__(self, args):
        """
        Initializes global shared properties
        :param args: Arguments passed in from user, collected from ArgParse
        """
        self._mgmt_session = None
        self._s3_resource = None
        self._mgmt_ssm = None
        self._profile = None
        self._command_factory = None
        self._session_manager = None
        self._is_setup_command: bool = FiggyCLI.is_setup_command(args)
        self._utils = Utils(self.get_colors_enabled())
        self._sts = boto3.client('sts')
        self._defaults: CLIDefaults = FiggyCLI.get_defaults(skip=self._is_setup_command)
        self._run_env = self._defaults.run_env
        role_override = Utils.attr_if_exists(role, args)
        self._role: Role = self.get_role(args.prompt, role_override=role_override)

        if args.version is False and args.configure is False:
            if not hasattr(args, 'env') or args.env is None:
                print(f"{EMPTY_ENV_HELP_TEXT}{self._run_env.env}")
            else:
                Utils.stc_validate(args.env in self._defaults.valid_envs,
                                   f'{ENV_HELP_TEXT} {self._defaults.valid_envs}. Provided: {args.env}')
                self._run_env = RunEnv(args.env)

        self._utils.validate(Utils.attr_exists(configure, args) or Utils.attr_exists(command, args),
                             f"No command found. Proper format is `{CLI_NAME} <resource> <command> --option(s)`")

        self._assumable_role = self.find_assumable_role(self._run_env, self._role, skip=self._is_setup_command)
        #Todo validate this role?

        command_val = Utils.attr_if_exists(command, args)
        resource_val = Utils.attr_if_exists(resource, args)
        found_command: frozenset = frozenset({Utils.attr_if_exists(command, args)}) if command_val else None
        found_resource: frozenset = frozenset({Utils.attr_if_exists(resource, args)}) if resource_val else None

        self._context = FiggyContext(self.get_colors_enabled(), found_resource, found_command,
                                     self._run_env, self._assumable_role, args)

    def _get_session_manager(self):
        """
        Lazy load a hydrated session manager. This supports error reporting, auto-upgrade functionality, etc.
        """
        if not self._session_manager:
            self._session_manager = SessionManager(self.get_colors_enabled(),
                                                   self.get_defaults(skip=self._is_setup_command),
                                                   self._get_session_provider())

        return self._session_manager

    def _get_session_provider(self):
        if not self._session_provider:
            self._session_provider = SessionProviderFactory(self.get_defaults(skip=self._is_setup_command)).instance()

        return self._session_provider

    def get_command_factory(self) -> CommandFactory:
        if not self._command_factory:
            self._command_factory = CommandFactory(self._context, self.get_defaults(skip=self._is_setup_command))

        return self._command_factory


def main():
    """
        Entrypoint to figgy.

        Performs generic validation, then routes user down appropriate execution path based on command line parameters
    """
    arguments = sys.argv
    user = getpass.getuser()
    Utils.stc_validate(user != ROOT_USER, f"Hey! Stop trying to run {CLI_NAME} as {ROOT_USER}. That's bad!")

    original_command = ' '.join(arguments)
    sys.argv = arguments
    try:
        # Parse / Validate Args
        args = FiggyCLI.parse_args()
        if hasattr(args, 'debug') and args.debug:
            root_logger.setLevel(logging.INFO)
            root_logger.addHandler(stdout_handler)

        cli: FiggyCLI = FiggyCLI(args)
        command: Command = cli.get_command()

        if hasattr(args, 'info') and args.info:
            command.print_help_text()
        else:
            command.execute()

    except AssertionError as e:
        Utils.stc_error_exit(e.args[0])
    except Exception as e:
        try:
            error_reporter = FiggyErrorReporter(FiggyCLI.get_defaults())
            error_reporter.log_error(original_command, e)
        except Exception as e:
            print(e)
            print(f"\n\nUnable to log or report this exception. Please submit a Github issue to: {FIGGY_GITHUB}")
    except KeyboardInterrupt:
        exit(1)


if __name__ == '__main__':
    try:
        main()
    except Warning:
        pass
