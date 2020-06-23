import pexpect
import sys
from figcli.test.cli.config import *
from figcli.test.cli.dev.sync import DevSync
from figcli.test.cli.figgy import FiggyTest
from figcli.utils.utils import *


class DevCleanup(FiggyTest):

    def __init__(self, extra_args=""):
        super().__init__(None, extra_args=extra_args)
        self.missing_key = '/app/ci-test/v1/config12'

    def run(self):
        # self.cleanup_success()
        # time.sleep(10)
        self.cleanup_with_orphans()

    def prep_success(self):
        sync = DevSync(extra_args=self.extra_args)
        sync.prep_sync()
        sync.sync_success()

    def prep_with_orphans(self):
        sync = DevSync(extra_args=self.extra_args)
        sync.sync_with_orphans()

    def cleanup_success(self):
        self.prep_success()
        self.step(f"Testing: {CLI_NAME} config {Utils.get_first(cleanup)} --env {DEFAULT_ENV} "
              f"--config figcli/test/assets/success/figgy.json --skip-upgrade ")
        time.sleep(30)
        child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(cleanup)} --env {DEFAULT_ENV} '
                                    f'--config figcli/test/assets/success/figgy.json --skip-upgrade {self.extra_args}',
                                    encoding='utf-8', timeout=10)
        child.expect('.*No orphaned keys.*No remote replication configs.*')
        child.logfile = sys.stdout
        print("Empty cleanup, success!")

    def cleanup_with_orphans(self):
        self.prep_with_orphans()
        self.step(f"Testing: {CLI_NAME} config {Utils.get_first(cleanup)} --env {DEFAULT_ENV} "
              f"--config figcli/test/assets/error/figgy.json")

        time.sleep(30)
        child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(cleanup)} --env {DEFAULT_ENV} '
                                    f'--config figcli/test/assets/error/figgy.json --skip-upgrade {self.extra_args}',
                                    encoding='utf-8', timeout=10)
        child.logfile = sys.stdout
        child.expect('.*/app/ci-test/v1/config11.* exists.*but does not exist.*')
        child.sendline('n')
        child.expect('.*does not exist in your.*')
        child.sendline('n')
        print("Cleanup with orphans success!")