import sys

import pexpect
from figcli.test.cli.config import *
from figcli.test.cli.dev.get import DevGet
from figcli.test.cli.dev.delete import DevDelete
from figcli.test.cli.dev.put import DevPut

from figcli.test.cli.figgy import FiggyTest
from figcli.config import *
from figcli.utils.utils import *
import uuid
import time


class DevSync(FiggyTest):

    def __init__(self, extra_args=""):
        super().__init__(None, extra_args=extra_args)
        self.missing_key = '/app/ci-test/v1/config12'

    def run(self):
        self.step("Preparing sync process...")
        self.prep_sync()
        self.step("Testing successful sync")
        self.sync_success()
        self.step("Testing multi-level sync")
        self.sync_multi_level_success()
        self.step("Testing sync with known orphaned parameters.")
        self.sync_with_orphans()

    def prep_sync(self):
        put = DevPut(extra_args=self.extra_args)
        put.add('/app/ci-test/v1/config9', DELETE_ME_VALUE, desc='desc', add_more=True)
        put.add('/app/ci-test/v1/config11', DELETE_ME_VALUE, desc='desc', add_more=True)
        put.add('/shared/jordan/testrepl', DELETE_ME_VALUE, desc='desc', add_more=True)
        put.add('/shared/jordan/testrepl2', DELETE_ME_VALUE, desc='desc', add_more=True)
        put.add('/shared/jordan/testrepl3', DELETE_ME_VALUE, desc='desc', add_more=True)
        put.add('/shared/jordan/testrepl4', DELETE_ME_VALUE, desc='desc', add_more=False)
        print("EXECUTING DELETE!!!!")
        delete = DevDelete(extra_args=self.extra_args)
        delete.delete(self.missing_key)

    def sync_success(self):
        print(f"Testing: {CLI_NAME} config {Utils.get_first(sync)} --env {DEFAULT_ENV} "
              f"--config figcli/test/assets/success/figgy.json")
        child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(sync)} --env {DEFAULT_ENV} '
                              f'--config figcli/test/assets/success/figgy.json --skip-upgrade {self.extra_args}',
                              encoding='utf-8', timeout=10)
        child.logfile = sys.stdout
        missing_key = '/app/ci-test/v1/config12'
        child.expect(f'.*Please input a value for.*{missing_key}.*')
        child.sendline(DELETE_ME_VALUE)
        child.expect('.*optional description:.*')
        child.sendline('desc')
        child.expect('.*value a secret.*')
        child.sendline('n')
        child.expect('.*Sync completed with no errors!')

    def sync_multi_level_success(self):
        missing_key = '/app/dev/thing/ci-test2/app/ci-test/v1/config12'
        delete = DevDelete(extra_args=self.extra_args)
        delete.delete(missing_key)

        put = DevPut(extra_args=self.extra_args)
        put.add('/app/dev/thing/ci-test2/config9', DELETE_ME_VALUE, desc='desc', add_more=True)
        put.add('/app/dev/thing/ci-test2/config11', DELETE_ME_VALUE, desc='desc', add_more=True)
        put.add('/shared/jordan/testrepl', DELETE_ME_VALUE, desc='desc', add_more=True)
        put.add('/shared/jordan/testrepl2', DELETE_ME_VALUE, desc='desc', add_more=True)
        put.add('/shared/jordan/testrepl3', DELETE_ME_VALUE, desc='desc', add_more=True)
        put.add('/shared/jordan/testrepl4', DELETE_ME_VALUE, desc='desc', add_more=False)

        print(f"Testing: {CLI_NAME} config {Utils.get_first(sync)} --env {DEFAULT_ENV} "
              f"--config figcli/test/assets/success/multi-level-ns.json")
        child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(sync)} --env {DEFAULT_ENV} '
                              f'--config figcli/test/assets/success/multi-level-ns.json --skip-upgrade {self.extra_args}',
                              encoding='utf-8', timeout=10)

        child.expect(f'.*Please input a value for.*{missing_key}.*')
        child.sendline(DELETE_ME_VALUE)
        child.expect('.*optional description:.*')
        child.sendline('desc')
        child.expect('.*value a secret.*')
        child.sendline('n')
        child.expect('.*Sync completed with no errors!')

    def sync_with_orphans(self):
        delete = DevDelete(extra_args=self.extra_args)
        delete.delete(self.missing_key)
        print("Successful sync + cleanup passed!")

        print(f"Testing: {CLI_NAME} config {Utils.get_first(sync)} --env {DEFAULT_ENV} "
              f"--config figcli/test/assets/error/figgy.json")
        child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(sync)} --env {DEFAULT_ENV} '
                              f'--config figcli/test/assets/error/figgy.json --skip-upgrade {self.extra_args}', timeout=10)
        child.expect('.*Unused Parameter:.*/app/ci-test/v1/config11.*')
        print("Sync with orphaned configs passed!")
