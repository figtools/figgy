from utils.utils import *
from config import *
import getpass


class Input:
    """
    Contains some generic prompts that are used by multiple different executions paths in figgy
    """

    @staticmethod
    def select_aws_cli_profile() -> str:
        default_value = 'bastion'
        profile = input(
            f'Please input the aws_cli profile name of your first.last_programmatic user in the MGMT account (Default: {default_value}): ') or default_value
        Utils.stc_validate(profile != '', "You must input a valid aws_cli profile")

        return profile

    @staticmethod
    def get_okta_user() -> str:
        okta_username = input('Please input OKTA username: ')
        Utils.stc_validate(okta_username != '', "You must input a valid OKTA username")

        return okta_username

    @staticmethod
    def get_okta_password() -> str:
        okta_password = getpass.getpass('Please input OKTA password: ')
        Utils.stc_validate(okta_password != '', "You must input a valid OKTA password")

        return okta_password

    @staticmethod
    def select_role(valid_roles: List[str] = None) -> Role:
        input_role = prompt(f'What type of user are you? Options are: {valid_roles}: ',
                            completer=WordCompleter(valid_roles))

        if valid_roles:
            Utils.stc_validate(input_role in valid_roles,
                               f"{input_role} is not a valid user type. Please select from: {valid_roles}")

        return Role(input_role)

    @staticmethod
    def select_default_account(valid_envs: List[str] = None) -> RunEnv:
        environemnt = prompt(f'Please select a default account. Options are: {valid_envs}: ',
                               completer=WordCompleter(valid_envs))

        if valid_envs:
            Utils.stc_validate(environemnt in valid_envs,
                               f"{environemnt} is not a valid environment type. Please select from: {valid_envs}")

        return RunEnv(environemnt)

    @staticmethod
    def select_enable_colors() -> bool:
        selection = ''
        while selection.lower() != 'y' and selection.lower() != 'n':
            selection = input(f'Enable colored output? (Colors: {Color.fg_rd}RED{fg.rs} {Color.fg_bl}BLUE{fg.rs} '
                              f'{Color.fg_gr}GREEN{fg.rs} <-- If you see weirdness, select N) Y/n?: ')
            selection = selection.lower() if selection != '' else 'y'
        return selection == 'y'

    @staticmethod
    def get_mfa() -> str:
        mfa = input('Please input the MFA associated with your first.last_programmatic user in the MGMT account: ')
        Utils.stc_validate(mfa != '', "You must input a valid mfa")

        return mfa

    @staticmethod
    def get_okta_mfa() -> str:
        mfa = input('Please input the MFA associated with your OKTA account: ')
        Utils.stc_validate(mfa != '', "You must input a valid mfa")

        return mfa

    @staticmethod
    def select_run_env(valid_envs: List[str]) -> RunEnv:
        input_env = prompt(f'Select a RunEnvironment: {valid_envs}: ',
                           completer=WordCompleter(valid_envs))
        Utils.stc_validate(input_env in valid_envs,
                           f"{input_env} is not a valid Run Environment. Please select from: {valid_envs}")

        return RunEnv(input_env)
