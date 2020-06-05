import sys

import pexpect

from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.utils.utils import *


class DevCleanup(FiggyTest):

    def __init__(self):
        super().__init__(None)

    def run(self):
        self.cleanup_success()
        self.cleanup_with_orphans()

    def cleanup_success(self):
        self.step(f"Testing: {CLI_NAME} config {Utils.get_first(cleanup)} --env {DEFAULT_ENV} "
              f"--config figgy/test/assets/success/ci-config.json --skip-upgrade ")
        child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(cleanup)} --env {DEFAULT_ENV} '
                                    f'--config figgy/test/assets/success/ci-config.json --skip-upgrade',
                                    encoding='utf-8', timeout=10)
        child.expect('.*No orphaned keys.*No remote replication configs.*')
        print("Empty cleanup, success!")

    def cleanup_with_orphans(self):
        self.step(f"Testing: {CLI_NAME} config {Utils.get_first(cleanup)} --env {DEFAULT_ENV} "
              f"--config figgy/test/assets/error/ci-config.json")
        child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(cleanup)} --env {DEFAULT_ENV} '
                                    f'--config figgy/test/assets/error/ci-config.json --skip-upgrade',
                                    encoding='utf-8', timeout=10)
        child.expect('.*/app/ci-test/v1/config11.* exists.*but does not exist.*')
        child.sendline('n')
        child.expect('.*replication mapping.*does not exist.*')
        child.sendline('n')
        print("Cleanup with orphans success!")