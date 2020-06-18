import logging
import requests
import os
import json
import traceback
import datetime
import re
from figcli.config import *
from figcli.config.style.terminal_factory import TerminalFactory
from figcli.input import Input
from figcli.utils.utils import Utils

from figcli.models.defaults.defaults import CLIDefaults

log = logging.getLogger(__name__)


def obey_reporting_preference(function):
    """
    Do not execute this method if report_errors is disabled, even if someone tells you to!
    """

    def inner(self, *args, **kwargs):
        if not self.reporting_enabled:
            return None
        else:
            return function(self, *args, **kwargs)

    return inner


class FiggyErrorReporter:
    _SECRET_MATCHERS = [
        r'.*AKIA.*',  # Match for AWS access keys
        r'.*[pP][aA][sS][sS].*'  # Anything with pass(word), skip it.
    ]

    def __init__(self, cli_defaults: CLIDefaults):
        self._cli_defaults = cli_defaults
        self.c = TerminalFactory(self._cli_defaults.colors_enabled).instance().get_colors()
        self.reporting_enabled = cli_defaults.report_errors

    @staticmethod
    def sanitize(e: Exception):
        """
        FYI: There's no reason why there _should_ ever be a secret in a stack trace, but.. if.. somehow.. there is..
             then we want to abandon ship!

        Look for potential stack trace and wipe this baby clean if anything matches.
        :param e: Exception to sanitize and return a printable stack trace of
        :return: printable representation of the provided exception
        """
        printable_exception = ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))

        for matcher in FiggyErrorReporter._SECRET_MATCHERS:
            if re.match(matcher, printable_exception, re.MULTILINE):
                return f"Stacktrace wiped because matcher: {matcher} matched it. "

        return printable_exception

    @obey_reporting_preference
    def report_error(self, command: str, e: Exception) -> None:
        """
        If the user chooses to report this exception, ship it off over to the Figgy API to let us know what went wrong!
        :param command: user's command input
        :param e: exception that was thrown
        """

        printable_exception = self.sanitize(e)
        os = Utils.get_os()

        payload = {
            'command': command,
            'os': os,
            'stacktrace': printable_exception
        }

        result = requests.post(FIGGY_ERROR_REPORTING_URL, json=payload)

        Utils.stc_validate(result.status_code == 200, "Unable to report this error to Figgy. Please consider "
                                                      f"opening a ticket on the figgy github repo: {FIGGY_GITHUB}")

        print(f"We are so sorry you experienced this error! This error has been anonymously reported to the Figgy "
              f"development team. \n\nIf you don't want to be prompted to report errors, you can disable the error "
              f"reporting by running `{CLI_NAME} --configure`.")
        print(f"\n\n{self.c.fg_bl}--------------------------------------------------------{self.c.rs}\n\n")

    def log_error(self, command: str, e: Exception):
        os.makedirs(ERROR_LOG_DIR, exist_ok=True)

        # Do not sanitize here since this is only written to the user's local log folder.
        printable_exception = ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
        log_file_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S.log")

        with open(f'{ERROR_LOG_DIR}/{log_file_name}', "w+") as log:
            log.write(f'Command: {command}\n\n\n{printable_exception}')

        print(f"\n\n{self.c.fg_bl}---------------------ERROR ENCOUNTERED --------------------{self.c.rs}\n\n")
        print(f"{self.c.fg_rd}Figgy experienced the following irrecoverable error. "
              f"Please consider reporting this error.{self.c.rs}")
        print(printable_exception)

        print(f"\n\n{self.c.fg_bl}-----------------------------------------------------------{self.c.rs}\n\n")

        if self.reporting_enabled:
            ship_it = Input.y_n_input("Would you like to report this to Figgy's developer(s)?", default_yes=True)

            if ship_it:
                self.report_error(command, e)
            else:
                print(f"Error was not reported. Please consider reporting this error on our Github: "
                      f"{FIGGY_GITHUB}. Error details have been logged to this file: "
                      f"{self.c.fg_bl}{log_file_name}{self.c.rs}. Farewell! \n")
