import pexpect
from test.cli.config import *
from test.cli.dev.get import DevGet
from test.cli.dev.delete import DevDelete
from test.cli.dev.put import DevPut

from test.cli.figgy import FiggyTest
from config import *
from utils.utils import *
import uuid
import time


class DevSync(FiggyTest):

    def run(self):
        self.sync_success()
        self.sync_with_orphans()

    def sync_success(self):
        print(f"Testing: python figgy.py config {Utils.get_first(sync)} --env {dev} "
              f"--config test/assets/success/ci-config.json")
        child = pexpect.spawn(f'python figgy.py config {Utils.get_first(sync)} --env {dev} '
                                    f'--config test/assets/success/ci-config.json --skip-upgrade', timeout=10)
        missing_key = '/app/ci-test/v1/config12'
        child.expect(f'.*Please input a value for.*{missing_key}.*')
        child.sendline(DELETE_ME_VALUE)
        child.expect('.*optional description:.*')
        child.sendline('desc')
        child.expect('.*value a secret.*')
        child.sendline('n')
        child.expect('.*Sync completed with no errors!')
        delete = DevDelete()
        delete.delete(missing_key)
        print("Successful sync + cleanup passed!")

    def sync_with_orphans(self):
        print(f"Testing: python figgy.py config {Utils.get_first(sync)} --env {dev} "
              f"--config test/assets/error/ci-config.json")
        child = pexpect.spawn(f'python figgy.py config {Utils.get_first(sync)} --env {dev} '
                                    f'--config test/assets/error/ci-config.json --skip-upgrade', timeout=10)
        child.expect('.*Unused Parameter:.*/app/ci-test/v1/config11.*Orphaned replication.*/shared/jordan/testrepl2.*')
        print("Sync with orphaned configs passed!")
