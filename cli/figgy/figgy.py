import argparse
import os
import stat
import sys
import traceback
import getpass
from json import JSONDecodeError

import jsonpickle
import platform
import logging
from config import *
from typing import Optional, Tuple, List
from zipfile import ZipFile

import boto3
from botocore.errorfactory import ClientError

from extras.s3_download_progress import S3Progress
from input.input import Input, readline
from commands.command_factory import CommandFactory
from commands.figgy_context import FiggyContext
from commands.types.command import Command
from data.dao.ssm import SsmDao
from extras.completer import Completer
from models.assumable_role import AssumableRole
from models.defaults.defaults import CLIDefaults
from models.role import Role
from models.run_env import RunEnv
from svcs.cache_manager import CacheManager
from svcs.observability.error_reporter import FiggyErrorReporter
from svcs.sso.provider.provider_factory import SessionProviderFactory
from svcs.sso.session_manager import SessionManager
from utils.utils import Utils

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
        os.makedirs(os.path.dirname(DEFAULTS_FILE_PATH), exist_ok=True)

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
            defaults = self.get_defaults(self._configure_set)
            if defaults is not None and not prompt:
                return defaults.profile
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

        defaults = self.get_defaults(self._configure_set)
        if defaults is not None and not prompt:
            return defaults.role
        else:
            return Input.select_role()

    def get_colors_enabled(self) -> bool:
        """
        Defaults to true, unless user ran --configure and disabled colored output
        Returns: True/False

        """
        defaults = self.get_defaults(skip=self._configure_set)
        if defaults is not None:
            return defaults.colors_enabled
        else:
            return True

    def get_command(self) -> Command:
        """
        Maps the user's passed in text command to one of our defined 'command' objects we use in the code.
        Args:

        Returns: command object.
        """
        return self.get_command_factory().instance()

    def _install_mac_onedir(self, install_path: str, latest_version: str):
        s3_path = f'{CLI_NAME}/{latest_version}/{platform.system().lower()}/{CLI_NAME}.zip'

        try:
            total_bytes = self.get_s3_resource().Object(CLI_BUCKET, s3_path).content_length
            progress = S3Progress(total=total_bytes, unit='B', unit_scale=True, miniters=1, desc='Downloading')
            bucket = self.get_s3_resource().Bucket(CLI_BUCKET)
            zip_path = f"{HOME}/.{CLI_NAME}/{CLI_NAME}.zip"
            install_dir = f'{HOME}/.{CLI_NAME}/{CLI_NAME}/version/{latest_version}'

            os.makedirs(os.path.dirname(install_dir), exist_ok=True)

            with progress:
                bucket.download_file(s3_path, zip_path, Callback=progress)

            with ZipFile(zip_path, 'r') as zipObj:
                zipObj.extractall(install_dir)

            if self._utils.file_exists(install_path):
                os.remove(install_path)

            executable_path = f'{install_dir}/{CLI_NAME}'
            st = os.stat(executable_path)
            os.chmod(executable_path, st.st_mode | stat.S_IEXEC)
            os.symlink(f'{install_dir}/{CLI_NAME}', install_path)
            print(f'{CLI_NAME} has been installed at path `{install_path}`.')
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("Unable to find the {CLI_NAME} in S3. Something went terribly wrong! :(")
            else:
                raise

    def _perform_upgrade(self, latest_version: str) -> None:
        """
        Walks the user through the upgrade path. Supports Windows/Linux/& OSX for Windows we must rename the running
        binary to a different name, as we cannot overwrite the existing running binary.
        Args:
            latest_version: str: The version ot upgrade to, i.e 1.0.6
            mgmt_session: Session that may be leveraged for performing the upgrade by downloading the appropriate binary
                          from S3.
        """
        readline.parse_and_bind("tab: complete")
        comp = Completer()
        readline.set_completer_delims(' \t\n')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(comp.pathCompleter)
        abs_path = os.path.dirname(sys.executable)
        install_path = input(f'Input path to your existing installation. Default: {abs_path} : ') or abs_path
        suffix = ".exe" if self._utils.is_windows() else ""

        if os.path.isdir(install_path):
            if install_path.endswith('/'):
                install_path = install_path[:-1]

            install_path = f"{install_path}/{CLI_NAME}{suffix}"

        if not self._utils.file_exists(install_path):
            self._utils.error_exit("Invalid install path specified, try providing the full path to the binary.")

        print(f"Install path: {install_path}")
        s3_path = f'{CLI_NAME}/{latest_version}/{platform.system().lower()}/{CLI_NAME}{suffix}'
        print(f"Installing: {CLI_NAME}/{latest_version}/{platform.system().lower()}/{CLI_NAME}{suffix}")
        print(f"{self.c.fg_bl}Downloading `{CLI_NAME}` version: {latest_version}{self.c.rs}")

        old_path = f'{install_path}.OLD'
        temp_path = install_path + "tmp"

        if self._utils.file_exists(old_path):
            os.remove(old_path)
        if self._utils.file_exists(temp_path):
            os.remove(temp_path)
        if self._utils.file_exists(install_path):
            os.rename(install_path, old_path)

        if not Utils.is_mac():
            try:
                total_bytes = self.get_s3_resource().Object(CLI_BUCKET, s3_path).content_length
                progress = S3Progress(total=total_bytes, unit='B', unit_scale=True, miniters=1, desc='Downloading')
                bucket = self.get_s3_resource().Bucket(CLI_BUCKET)

                with progress:
                    bucket.download_file(s3_path, temp_path, Callback=progress)

            except ClientError as e:
                if e.response['Error']['Code'] == "404":
                    print("Unable to find the {CLI_NAME} in S3. Something went terribly wrong! :(")
                else:
                    raise
            else:
                st = os.stat(temp_path)
                os.chmod(temp_path, st.st_mode | stat.S_IEXEC)
                os.rename(temp_path, install_path)
        else:
            self._install_mac_onedir(f'{install_path}', latest_version)

            print(f"{self.c.fg_gr}Installation successful! Exiting. Rerun `{CLI_NAME}` "
                  f"to use the latest version!{self.c.rs}")
            exit()

    def find_assumable_roles(self, env: RunEnv, role: Role, skip: bool = False) -> Tuple[AssumableRole, AssumableRole]:
        matching_role, next_role = None, None
        assumable_roles: List[AssumableRole] = self.get_defaults(skip=skip).assumable_roles
        matching_role = [ar for ar in assumable_roles if ar.role == role and ar.run_env == env]
        if matching_role:
            matching_role = matching_role.pop()
            next_idx = assumable_roles.index(matching_role) + 1
            next_role = assumable_roles[next_idx] if next_idx < len(assumable_roles) else None
        return matching_role, next_role

    def check_version(self):
        """
        Looks up the current latest version from P.S. Offers automated installation if possible, otherwise tells user
        how to manually install themselves.
        :return:
        """
        mgmt_session = self.get_mgmt_session()

        if mgmt_session:
            latest_version = self.get_mgmt_ssm().get_parameter(CLI_LATEST_VERSION_PS_PATH)

            if VERSION != latest_version:
                print(f"{self.c.fg_rd}Your version of the `{CLI_NAME}` is out of date. You are running "
                      f"{self.c.rs}{self.c.fg_bl}{VERSION}{self.c.rs} instead of "
                      f"{self.c.fg_bl}{latest_version}{self.c.rs}\n")
                selection = input(f"W ould you like to try the auto-upgrade? This should work for "
                                  f"Linux/OS-X/Windows installations. (Y/n): ")
                selection = selection if selection != '' else 'y'
                if selection.lower() == "y":
                    self._perform_upgrade(latest_version)
                else:
                    suffix = ""
                    command = CLI_UPDATE_COMMAND.replace('$$VERSION$$', latest_version) \
                        .replace('$$OS$$', platform.system().lower())

                    if self._utils.is_windows():
                        suffix = ".exe"

                    command = command.replace('$$SUFFIX$$', suffix)
                    print("You can still manual upgrade. To download the latest version run this "
                          f"command: {command}\nYou will need to add {CLI_NAME} to your path manually.")

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
        self._configure_set: bool = Utils.is_set_true(configure, args)
        self.c = Color(self.get_colors_enabled())
        self._utils = Utils(self.get_colors_enabled())
        self._sts = boto3.client('sts')
        self._defaults: CLIDefaults = FiggyCLI.get_defaults(skip=self._configure_set)
        self._run_env = self._defaults.run_env
        role_override = Utils.attr_if_exists(role, args)
        self._role: Role = self.get_role(args.prompt, role_override=role_override)

        if not hasattr(args, 'env') or args.env is None:
            print(f"{EMPTY_ENV_HELP_TEXT}{self._run_env.env}")
        else:
            Utils.stc_validate(args.env in self._defaults.valid_envs,
                               f'{ENV_HELP_TEXT} {self._defaults.valid_envs}. Provided: {args.env}')
            self._run_env = RunEnv(args.env)

        self._utils.validate(Utils.attr_exists(configure, args) or Utils.attr_exists(command, args),
                                f"No command found. Proper format is `{CLI_NAME} <resource> <command> --option(s)`")

        self._assumable_role, self._next_assumable_role = self.find_assumable_roles(self._run_env, self._role,
                                                                                    skip=self._configure_set)

        command_val = Utils.attr_if_exists(command, args)
        resource_val = Utils.attr_if_exists(resource, args)
        found_command: frozenset = frozenset({Utils.attr_if_exists(command, args)}) if command_val else None
        found_resource: frozenset = frozenset({Utils.attr_if_exists(resource, args)}) if resource_val else None

        log.info(f"Command {found_command}, resource: {found_resource}")

        self._context = FiggyContext(self.get_colors_enabled(), found_resource, found_command,
                                     self._run_env, self._assumable_role, self._next_assumable_role, args)
        # Todo: Solve for auto-upgrade in future & Solve for mgmt sessions
        # if not self._context.skip_upgrade:
        #     self.check_version()

    def _get_session_manager(self):
        """
        Lazy load a hydrated session manager. This supports error reporting, auto-upgrade functionality, etc.
        """
        if not self._session_manager:
            self._session_manager = SessionManager(self.get_colors_enabled(),
                                                   self.get_defaults(skip=self._configure_set),
                                                   self._get_session_provider())

        return self._session_manager

    def _get_session_provider(self):
        if not self._session_provider:
            self._session_provider = SessionProviderFactory(self.get_defaults(skip=self._configure_set)).instance()

        return self._session_provider

    def get_command_factory(self) -> CommandFactory:
        if not self._command_factory:
            self._command_factory = CommandFactory(self._context, self.get_defaults(skip=self._configure_set))

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
            exit(0)

        command.execute()
    except AssertionError as e:
        Utils.stc_error_exit(e.args[0])
    except Exception as e:
        try:
            error_reporter = FiggyErrorReporter(FiggyCLI.get_defaults())
            error_reporter.log_error(original_command, e)
        except Exception:
            print(e)
            print(f"Unable to log or report this exception. Please submit a Github issue to: {FIGGY_GITHUB}")
    except KeyboardInterrupt:
        exit(1)




if __name__ == '__main__':
    try:
        main()
    except Warning:
        pass
