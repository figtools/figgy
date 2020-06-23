from dataclasses import dataclass
from typing import Optional, Tuple, Dict
import requests
import logging
import random
import re
from figcli.config.constants import *
from figcli.config.style.color import Color
from figcli.config.style.terminal_factory import TerminalFactory
from figcli.models.defaults.defaults import CLIDefaults

log = logging.getLogger(__name__)


@dataclass
class FiggyVersionDetails:
    version: str
    notify_chance: int
    changelog: str

    def changes_from(self, old_version: str):
        regex = f'.*(##+\s+{self.version}.*)##+\s+{old_version}.*'
        result = re.match(regex, self.changelog, re.DOTALL)
        if result:
            return result.group(1).rstrip()
        else:
            return f"Unable to parse changes for new version: {self.version}"

    @staticmethod
    def from_api_response(response: Dict) -> "FiggyVersionDetails":
        notify_chance, version, changelog = \
            response.get('notify_chance'), response.get('version'), response.get('changelog')

        if not notify_chance or notify_chance == 'None':
            notify_chance = 0

        if not version:
            raise ValueError('No valid version found.')
        elif not changelog:
            raise ValueError('No valid changelog found.')

        return FiggyVersionDetails(
            version=version,
            notify_chance=int(notify_chance),
            changelog=response.get('changelog')
        )


class VersionTracker:
    _UPGRADE_CHECK_PERCENTAGE = 5  # % chance any decorated method execution will check for an upgrade

    def __init__(self, cli_defaults: CLIDefaults):
        self._cli_defaults = cli_defaults
        self.c = TerminalFactory(self._cli_defaults.colors_enabled).instance().get_colors()

    @staticmethod
    def get_version() -> FiggyVersionDetails:
        result = requests.get(FIGGY_GET_VERSION_URL)
        if result.status_code == 200:
            details: FiggyVersionDetails = FiggyVersionDetails.from_api_response(result.json())
            return details
        else:
            raise ValueError("Unable to fetch figgy version details.")

    @staticmethod
    def check_version(c: Color) -> None:
        try:
            new_details = VersionTracker.get_version()

            if new_details.version != VERSION:
                VersionTracker.print_new_version_msg(c, new_details)
                VersionTracker.print_changes(c, new_details)
            else:
                print(f"Version: {VERSION}.")
                print(f"You are currently running the latest version of figgy.")

        except ValueError as e:
            log.warning("Unable to fetch version information from remote endpoint.")
            print(f"Version: {VERSION}")

    @staticmethod
    def print_changes(c: Color, new_details: FiggyVersionDetails) -> None:
        if new_details.version != VERSION:
            print(f'\n\n{c.fg_yl}Changes you\'ll get if you upgrade!{c.rs}')
            print(f'{c.fg_bl}------------------------------------------{c.rs}')
            print(new_details.changes_from(VERSION))
            print(f'{c.fg_bl}------------------------------------------{c.rs}')

    @staticmethod
    def print_new_version_msg(c: Color, new_details: FiggyVersionDetails):
        if not VersionTracker.is_rollback(VERSION, new_details.version):
            print(f'\n{c.fg_bl}------------------------------------------{c.rs}')
            print(f'A new version of figgy is available!')
            print(f"Current Version: {c.fg_yl}{VERSION}{c.rs}")
            print(f"New Version: {c.fg_bl}{new_details.version}{c.rs}")
            print(f"To see what the new version has in store for you, run `{CLI_NAME} --version`")
            print(f"To upgrade, run `brew upgrade {BREW_FORMULA}` or `pip install figgy-cli --upgrade`")
            print(f'{c.fg_bl}------------------------------------------{c.rs}')
        else:
            print(f'\n{c.fg_bl}------------------------------------------{c.rs}')
            print(f'Figgy was rolled back due to an issue and you\'re on a bad version!')
            print(f"Current Version: {c.fg_yl}{VERSION}{c.rs}")
            print(f"Recommended Version: {c.fg_bl}{new_details.version}{c.rs}")
            print(f"To roll-back, run `brew upgrade {BREW_FORMULA}` or `pip install figgy-cli --upgrade`")
            print(f'{c.fg_bl}------------------------------------------{c.rs}')

    @staticmethod
    def is_rollback(current_version: str, new_version: str):
        try:
            cu_major = current_version.split('.')[0]
            cu_minor = current_version.split('.')[1]
            cu_patch = current_version.split('.')[2].strip('ab')
            new_major = new_version.split('.')[0]
            new_minor = new_version.split('.')[1]
            new_patch = new_version.split('.')[2].strip('ab')

            if new_major < cu_major:
                return True
            elif new_major <= cu_major and new_minor < cu_minor:
                return True
            elif new_major <= cu_major and new_minor <= cu_minor and new_patch < cu_patch:
                return True
            else:
                return False
        except IndentationError:
            pass

    @staticmethod
    def upgrade_available(current_version: str, new_version: str):
        try:
            cu_major = current_version.split('.')[0]
            cu_minor = current_version.split('.')[1]
            cu_patch = current_version.split('.')[2].strip('ab')
            new_major = new_version.split('.')[0]
            new_minor = new_version.split('.')[1]
            new_patch = new_version.split('.')[2].strip('ab')

            if new_major > cu_major:
                return True
            elif new_major >= cu_major and new_minor > cu_minor:
                return True
            elif new_major >= cu_major and new_minor >= cu_minor and new_patch > cu_patch:
                return True
            else:
                return False
        except IndentationError:
            pass

    @staticmethod
    def notify_user(function):
        """
        Has a _chance_ to notify a user if a new version has been released and they are on the old version.
        """

        log.info("Rolling dice for update notify chance")

        def inner(self, *args, **kwargs):
            log.info("Rolling dice to check version..")
            if VersionTracker._UPGRADE_CHECK_PERCENTAGE > random.randint(0, 99):
                log.info("Checking for new version..")
                try:
                    details = VersionTracker.get_version()
                    if details.notify_chance > random.randint(0, 99) and details.version != VERSION:
                        log.info("Notifying user of new version")
                        if hasattr(self, 'c') and isinstance(self.c, Color):
                            VersionTracker.print_new_version_msg(self.c, details)
                except ValueError:
                    log.warning("Unable to fetch version information from remote resource.")

            return function(self, *args, **kwargs)

        return inner
