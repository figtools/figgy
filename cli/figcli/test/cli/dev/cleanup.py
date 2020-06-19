import sys

import pexpect

from figcli.test.cli.config import *
from figcli.test.cli.figgy import FiggyTest
from figcli.utils.utils import *


class DevCleanup(FiggyTest):

    def __init__(self, extra_args=""):
        super().__init__(None, extra_args=extra_args)

    def run(self):
        self.cleanup_success()
        self.cleanup_with_orphans()

    def cleanup_success(self):
        self.step(f"Testing: {CLI_NAME} config {Utils.get_first(cleanup)} --env {DEFAULT_ENV} "
              f"--config figcli/test/assets/success/figgy.json --skip-upgrade ")
        child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(cleanup)} --env {DEFAULT_ENV} '
                                    f'--config figcli/test/assets/success/figgy.json --skip-upgrade {self.extra_args}',
                                    encoding='utf-8', timeout=10)
        child.expect('.*No orphaned keys.*No remote replication configs.*')
        print("Empty cleanup, success!")

    def cleanup_with_orphans(self):
        self.step(f"Testing: {CLI_NAME} config {Utils.get_first(cleanup)} --env {DEFAULT_ENV} "
              f"--config figcli/test/assets/error/figgy.json")
        child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(cleanup)} --env {DEFAULT_ENV} '
                                    f'--config figcli/test/assets/error/figgy.json --skip-upgrade {self.extra_args}',
                                    encoding='utf-8', timeout=10)
        child.expect('.*/app/ci-test/v1/config11.* exists.*but does not exist.*')
        child.sendline('n')
        child.expect('.*replication mapping.*does not exist.*')
        child.sendline('n')
        print("Cleanup with orphans success!")