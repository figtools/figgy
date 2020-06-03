import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *


class DevZip(FiggyTest):

    def __init__(self):
        self._child = pexpect.spawn(f'python figgy.py {Utils.get_first(s3)} {Utils.get_first(zip)} '
                                    f'--env {dev} --skip-upgrade', timeout=5)
        self._child.delayafterread = .01
        self._child.delaybeforesend = .5

    def run(self):
        self.find()

    def find(self):
        print(f"Testing s3 zip.")
        self._child.expect('.*Select a bucket to zip from.*', timeout=15)
        self._child.sendline('figgy-test-bucket')
        self._child.expect('.*Please select a folder to search.*', timeout=60)
        self._child.sendline('toolbox-ui/fonts/')
        self._child.expect('.*Zip successfully generated at path.*', timeout=10)
        print("`figgy s3 zip` passed.")
