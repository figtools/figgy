import sys

import pexpect

from figcli.test.cli.config import *
from figcli.test.cli.dev.delete import DevDelete
from figcli.test.cli.dev.sync import DevSync
from figcli.test.cli.figgy import FiggyTest
from figcli.utils.utils import *


class DevValidate(FiggyTest):

    def __init__(self):
        super().__init__(None)
        self.missing_key = '/app/ci-test/v1/config12'

    def run(self):
        self.step("Testing successful validate.")
        self.validate_success()
        self.step("Testing validate with errors")
        self.validate_error()

    def validate_success(self):
        sync = DevSync()
        sync.sync_success()

        print(f"Testing: {CLI_NAME} config {Utils.get_first(validate)} --env {DEFAULT_ENV} "
              f"--config figgy/test/assets/success/figgy.json")
        child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(validate)} --env {DEFAULT_ENV} '
                              f'--config figgy/test/assets/success/figgy.json --skip-upgrade',
                              encoding='utf-8', timeout=10)
        child.logfile = sys.stdout
        child.expect(".*Success.*")

    def validate_error(self):
        delete = DevDelete()
        delete.delete(self.missing_key)
        print(f"Testing: {CLI_NAME} config {Utils.get_first(validate)} --env {DEFAULT_ENV} "
              f"--config figgy/test/assets/error/figgy.json")
        child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(validate)} --env {DEFAULT_ENV} '
                              f'--config figgy/test/assets/error/figgy.json --skip-upgrade', timeout=10)
        child.expect('.*missing at least one.*')
