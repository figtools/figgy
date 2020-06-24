from typing import Optional

from figcli.models.role import Role
from figcli.models.run_env import RunEnv
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from figcli.models.defaults.provider import Provider
from figcli.utils.utils import *
from figcli.config import *
import random
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
    def get_user(provider: str = 'Please input') -> str:
        okta_username = input(f'{provider} username: ')
        Utils.stc_validate(okta_username != '', "You must input a valid OKTA username")

        return okta_username

    @staticmethod
    def get_password(provider: str = 'Please input') -> str:
        okta_password = getpass.getpass(f'{provider} password: ')
        Utils.stc_validate(okta_password != '', "You must input a valid OKTA password")

        return okta_password

    @staticmethod
    def select_role(valid_roles: List[str]) -> Role:
        input_role = None
        while input_role not in valid_roles:
            input_role = prompt(f'What type of user are you? Options are: {valid_roles}: \n -> ',
                                completer=WordCompleter(valid_roles))
            if input_role not in valid_roles:
                print(f"{input_role} is not a valid user type. Please select from: {valid_roles}")

        return Role(input_role)

    @staticmethod
    def select_region() -> str:
        region = None
        while region not in AWS_REGIONS:
            region = prompt('Please input the AWS region to associate figgy with: ',
                            completer=WordCompleter(AWS_REGIONS))

            if region not in AWS_REGIONS:
                print(f"{region} is not a valid AWS Region, please choose from: {AWS_REGIONS}")

        return region

    @staticmethod
    def select_default_account(valid_envs: List[str]) -> RunEnv:
        environment = None
        while environment not in valid_envs:
            environment = prompt(f'Please select a default account. All commands without the specified `--env` '
                                 f'parameter will run against this account. \n Options are: {valid_envs}: \n -> ',
                                 completer=WordCompleter(valid_envs))

            if environment not in valid_envs:
                print(f"{environment} is not a valid environment type. Please select from: {valid_envs}")

        return RunEnv(environment)

    @staticmethod
    def select_enable_colors() -> bool:
        selection = ''
        c = TerminalFactory(True).instance().get_colors()
        while selection.lower() != 'y' and selection.lower() != 'n':
            selection = input(f'Enable colored output? (Colors: {c.fg_rd}RED{c.rs} {c.fg_bl}BLUE{c.rs} '
                              f'{c.fg_gr}GREEN{c.rs} <-- If you see weirdness, select N) Y/n?: ')
            selection = selection.lower() if selection != '' else 'y'
        return selection == 'y'

    @staticmethod
    def select_mfa_enabled() -> bool:
        selection = ''
        while selection.lower() != 'y' and selection.lower() != 'n':
            selection = input(f'Use Multi-factor authentication Y/n?: ')
            selection = selection.lower() if selection != '' else 'y'

        return selection == 'y'

    @staticmethod
    def select_auto_mfa() -> bool:
        return Input.y_n_input('Would you like to save your MFA secret to your keychain and have Figgy generate '
                               f'one time pass codes on your behalf? ', default_yes=False)

    @staticmethod
    def get_mfa_secret() -> str:
        print(f"You have selected that you would like to have `{CLI_NAME}` auto-generate one-time pass codes for you. "
              f"This is going to save you a lot of time, but we'll need to save your MFA secret to your OS keychain.\n"
              f"\nYour keychain secret is a text string that looks something like this: `LYV5Z1SNBM4KKUZO`. This "
              f"is the text representation of the QR Code you would would scan. \n\n")
        secret = input('Please input your MFA secret: -> ')
        return secret

    @staticmethod
    def select_report_errors() -> bool:
        selection = ''
        while selection.lower() != 'y' and selection.lower() != 'n':
            selection = input(f'Help make Figgy better. turn on anonymous error reporting?  Y/n?: ')
            selection = selection.lower() if selection != '' else 'y'
        return selection == 'y'

    @staticmethod
    def select_usage_tracking() -> bool:
        selection = ''
        while selection.lower() != 'y' and selection.lower() != 'n':
            selection = input(f'Help make Figgy better. Turn on 100% anonymous usage reporting Y/n?: ')
            selection = selection.lower() if selection != '' else 'y'
        return selection == 'y'

    @staticmethod
    def select_provider() -> Provider:
        selection = Provider.UNSELECTED
        completer = WordCompleter(words=Provider.names())
        while selection is Provider.UNSELECTED:
            selection = prompt(f'Please select an authentication provider. Options are: {Provider.names()}: ',
                               completer=completer)
            selection = Provider.new(selection)

        return selection

    @staticmethod
    def get_mfa(display_hint: bool = False, color: Optional[Color] = None) -> str:
        if display_hint and random.randint(0, 10) == 10:
            blue = color.fg_bl if color else ''
            rs = color.rs if color else ''
            print(f"{blue}Hint:{rs} Tired of typing in your MFA? Consider saving your MFA secret to your keychain and "
                  f"let {CLI_NAME} securely auto-generate tokens for you. \n"
                  f"{blue}More info:{rs} http://figgy.dev/docs/getting-started/install.html\n\n")

        mfa = input('Please input the MFA associated with your user: ')
        Utils.stc_validate(mfa != '', "You must input a valid mfa")

        return mfa

    @staticmethod
    def select_kms_key(valid_keys: List[str]) -> str:
        return Input.select("Select an encryption key: ", valid_options=valid_keys)

    @staticmethod
    def select_run_env(valid_envs: List[str]) -> RunEnv:
        input_env = prompt(f'Select a RunEnvironment: {valid_envs}: ',
                           completer=WordCompleter(valid_envs))
        Utils.stc_validate(input_env in valid_envs,
                           f"{input_env} is not a valid Run Environment. Please select from: {valid_envs}")

        return RunEnv(input_env)

    @staticmethod
    def is_secret() -> bool:
        return Input.y_n_input("Is this value a secret?", default_yes=False)

    @staticmethod
    def input(message: str, completer=None, default: str = None, optional: bool = False, min_length=0) -> str:
        loop = True
        message = f'\n{message}\n  -> ' if len(message) > 15 else f'\n{message} -> '

        while loop:
            if completer:
                result = prompt(message, completer=completer)
            elif default:
                result = prompt(message, default=default)
            else:
                result = input(message)

            if optional:
                return result

            if len(result) < min_length:
                print(f"\nInvalid input. it must be at least {min_length} characters in length.\n")
                result = None

            loop = not result or result.strip() == ''

        return result

    @staticmethod
    def y_n_input(message: str, default_yes: bool = True, invalid_no=False) -> bool:
        """
        Returns True if user selects 'y', or False if user select 'N'
        :param message: Message to prompt the user with.
        :param default_yes: Make the user's default option 'Y'?
        :param invalid_no: If the user enters invalid input, assume a selection of 'N'
        :return: True/False based on user input
        """

        selection = ''
        default_compare = 'y' if default_yes else 'n'
        default_prompt = '(Y/n)' if default_yes else '(y/N)'
        prompt_msg = f'\n{message} \n {default_prompt}: -> '

        while selection.lower() != 'y' and selection.lower() != 'n':
            selection = prompt(prompt_msg, completer=WordCompleter(['y', 'n'])).strip().lower()
            selection = selection.lower() if selection != '' else default_compare

            if selection != 'y' and selection != 'n' and invalid_no:
                return False

        print()
        return True if selection == 'y' else False

    @staticmethod
    def select(message: str, valid_options: List[str], default: str = None) -> str:
        """
        Returns the user's selection based on the provided valid options.
        :param message: Message to prompt the user with.
        :param valid_options: List of valid options to accept.
        :param default: Set the prompt's default to this
        :return: Selected option
        """
        selection = ''
        msg = f'{message}\nOptions: {valid_options}\n -> ' if len(valid_options) < 10 else f'{message} -> '
        while not selection:
            if default:
                selection = prompt(msg, completer=WordCompleter(words=valid_options, match_middle=True), default=default)
            else:
                selection = prompt(msg, completer=WordCompleter(words=valid_options))

            if selection not in valid_options:
                selection = ''

        print()
        return selection
