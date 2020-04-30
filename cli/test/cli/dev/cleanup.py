import pexpect
from test.cli.figgy import FiggyTest
from config import *
from utils.utils import *
import uuid
import time


class DevCleanup(FiggyTest):

    def run(self):
        self.cleanup_success()
        self.cleanup_with_orphans()

    def cleanup_success(self):
        print(f"Testing: python figgy.py config {Utils.get_first(cleanup)} --env {dev} "
              f"--config test/assets/success/ci-config.json --skip-upgrade ")
        child = pexpect.spawn(f'python figgy.py config {Utils.get_first(cleanup)} --env {dev} '
                                    f'--config test/assets/success/ci-config.json --skip-upgrade', timeout=10)
        child.expect('.*No orphaned keys.*No remote replication configs.*')
        print("Empty cleanup, success!")

    def cleanup_with_orphans(self):
        print(f"Testing: python figgy.py config {Utils.get_first(cleanup)} --env {dev} "
              f"--config test/assets/error/ci-config.json")
        child = pexpect.spawn(f'python figgy.py config {Utils.get_first(cleanup)} --env {dev} '
                                    f'--config test/assets/error/ci-config.json --skip-upgrade', timeout=10)
        child.expect('.*/app/ci-test/v1/config11.* exists.*but does not exist.*')
        child.sendline('n')
        child.expect('.*replication mapping.*does not exist.*')
        child.sendline('n')
        print("Cleanup with orphans success!")