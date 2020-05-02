import sys
import traceback
import getpass
from config import *
from typing import Optional
from zipfile import ZipFile

import boto3
from botocore.errorfactory import ClientError

from input.input import Input
from commands.command_factory import CommandFactory
from commands.config.migrate import *
from commands.figgy_context import FiggyContext
from commands.types.command import Command
from commands.help.configure import Configure
from data.dao.ssm import SsmDao
from extras.completer import Completer
from models.defaults import CLIDefaults
from svcs.session_manager import SessionManager
from utils.secrets_manager import SecretsManager

root_logger = logging.getLogger()
root_logger.setLevel(logging.CRITICAL)
root_logger.handlers = []
stdout_handler = logging.StreamHandler(sys.stdout)

log = logging.getLogger(__name__)


class Figgy:
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
                    Figgy.add_arg(com_parser, com_arg, cmd, rsc)

        return parser.parse_args()



    @staticmethod
    def get_defaults() -> Optional[CLIDefaults]:
        """Lookup a user's defaults as configured by --configure option.

        :return: hydrated CLIDefaults object of default values stored in cache file or None if no cache found
        """

        os.makedirs(os.path.dirname(DEFAULTS_FILE_PATH), exist_ok=True)

        try:
            with open(DEFAULTS_FILE_PATH, "r") as cache:
                contents = cache.read()
        except FileNotFoundError:
            Utils.stc_error_exit(f"{CLI_NAME.capitalize()} is unconfigured, please run `{CLI_NAME} "
                                 f"--{Utils.get_first(configure)}` before attempting any other commands")
        else:
            defaults: Dict = json.loads(contents)
            if not OKTA_USER_KEY in defaults:
                print("Figgy is now leveraging OKTA credentials, please reconfigure.")
                Figgy.configure()
                sys.exit(0)

            if defaults is not None:
                return CLIDefaults.from_dict(defaults)
            else:
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
            defaults = self.get_defaults()
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

        if DEFAULT_USER_NAME in os.environ \
                and os.environ[DEFAULT_USER_NAME] in user_types \
                and not prompt:
            return Role(os.environ.get(DEFAULT_USER_NAME))
        else:
            defaults = self.get_defaults()
            if defaults is not None and not prompt:
                return defaults.role
            else:
                return Input.select_role()

    def get_colors_enabled(self) -> bool:
        """
        Defaults to true, unless user ran --configure and disabled colored output
        Returns: True/False

        """
        defaults = self.get_defaults()
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

        :param run_env: dev/qa/stage/prod
        :param args: Arguments passed in from user, collected from ArgParse
        """
        self._mgmt_session = None
        self._s3_resource = None
        self._mgmt_ssm = None
        self._profile = None
        self._command_factory = None
        self._session_manager = None
        self.c = Color(self.get_colors_enabled())
        self._utils = Utils(self.get_colors_enabled())
        self._sts = boto3.client('sts')
        self._run_env = Figgy.get_defaults().run_env
        role_override = args.role if hasattr(args, 'role') else None
        self._selected_role: Role = self.get_role(args.prompt, role_override=role_override)

        if not hasattr(args, 'env') or args.env is None:
            print(f"{EMPTY_ENV_HELP_TEXT}{self._run_env.env}")
        else:
            Utils.stc_validate(Utils.valid_env(args.env), ENV_HELP_TEXT)
            self._run_env = RunEnv(args.env)


        # self._utils.validate(args.command is not None, "No command found. Proper format is "
        #                                                f"`{CLI_NAME} <resource> <command> --option(s)`")
        command_val = Utils.attr_if_exists(command, args)
        resource_val = Utils.attr_if_exists(resource, args)
        found_command: frozenset = frozenset({Utils.attr_if_exists(command, args)}) if command_val else None
        found_resource: frozenset = frozenset({Utils.attr_if_exists(resource, args)}) if resource_val else None

        log.info(f"Command {found_command}, resource: {found_resource}")

        self._context = FiggyContext(self.get_colors_enabled(), found_resource, found_command,
                                     self._run_env, self._selected_role, args)

        # Todo: Solve for auto-upgrade in future
        # if not self._context.skip_upgrade:
        #     self.check_version()

    def _get_session_manager(self):
        """
        Lazy load a hydrated session manager. This supports error reporting, auto-upgrade functionality, etc.
        """
        if not self._session_manager:
            self._session_manager = SessionManager(self.get_colors_enabled(), self.get_defaults())

        return self._session_manager

    def get_mgmt_session(self) -> boto3.session.Session:
        """
        Returns a hydrated mgmt session object. This is needed for auto-upgrade functionality
        :return: boto3.Session session for mgmt account.
        """
        if not self._mgmt_session:
            self._mgmt_session = self._session_manager.get_session(RunEnv(mgmt),
                                                                   self._context.selected_role,
                                                                   prompt=False, exit_on_fail=True)

        return self._mgmt_session

    def get_s3_resource(self) -> boto3.session.Session:
        """ :return: A mgmt account s3 resource """
        if not self._s3_resource:
            self._s3_resource = self.get_mgmt_session().resource('s3')

        return self._s3_resource

    def get_mgmt_ssm(self) -> SsmDao:
        """:return: hydrated mgmt account SsmDao """
        if not self._mgmt_ssm:
            self._mgmt_ssm = SsmDao(self.get_mgmt_session().client('ssm'))

        return self._mgmt_ssm

    def get_command_factory(self) -> CommandFactory:
        if not self._command_factory:
            self._command_factory = CommandFactory(self._context, self.get_defaults())

        return self._command_factory


def main(arguments):
    """
        Entrypoint to figgy.

        Performs generic validation, then routes user down appropriate execution path based on command line parameters
    """

    user = getpass.getuser()
    Utils.stc_validate(user != ROOT_USER, f"Hey! Stop trying to run {CLI_NAME} as {ROOT_USER}. That's bad!")

    sys.argv = arguments
    cli: Optional[Figgy] = None
    try:
        utils = Utils(False)
        # Parse / Validate Args
        args = Figgy.parse_args()
        if hasattr(args, 'debug') and args.debug:
            root_logger.setLevel(logging.INFO)
            root_logger.addHandler(stdout_handler)

        cli: Figgy = Figgy(args)
        command: Command = cli.get_command()

        if hasattr(args, 'info') and args.info:
            command.print_help_text()
            exit(0)

        command.execute()
    except AssertionError as e:
        Utils.stc_error_exit(e.args[0])
    except Exception as e:
        printable_exception = ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
        if cli is not None:
            mgmt_session = cli.get_mgmt_session()
            user = Figgy.get_defaults().okta_user or getpass.getuser()
            sns = mgmt_session.client('sns')
            sns_msg = f"The following exception has been caught by user {user}: \n\n{printable_exception}"
            sns.publish(TopicArn=MGMT_SNS_ERROR_TOPIC_ARN, Message=sns_msg, Subject=SNS_EMAIL_SUBJECT)
            print(f"Something went wrong. Exception caught:\n\n{printable_exception}\n\n"
                  f"This exception has been reported to DevOps")
        else:
            print(f"Something went wrong. Exception caught:\n\n{printable_exception}\n\n This exception "
                  f"could not be reported to DevOps automatically. Please inform us of this!")
    except KeyboardInterrupt:
        exit(1)


if __name__ == '__main__':
    try:
        main(sys.argv)
    except Warning:
        pass
