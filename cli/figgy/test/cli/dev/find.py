
import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *


class DevFind(FiggyTest):

    def __init__(self):
        self._child = pexpect.spawn(f'python figgy.py {Utils.get_first(s3)} {Utils.get_first(find)} '
                                    f'--env {dev} --skip-upgrade', timeout=5)
        self._child.delayafterread = .01
        self._child.delaybeforesend = .5

    def run(self):
        self.find()

    def find(self):
        print(f"Testing s3 find.")
        self._child.expect('.*Please select an S3 Bucket to search:.*', timeout=15)
        self._child.sendline('figgy-test-bucket')
        self._child.expect('.*Please select a folder to search.*', timeout=60)
        self._child.sendline('toolbox-ui/fonts/')
        self._child.expect('.*search folders matching a certain.*')
        self._child.sendline('n')
        self._child.expect('.*Please input your search criteria.*', timeout=5)
        self._child.sendline('*div*')
        self._child.expect('.*Files.*Matches.*0.*Misses.*', timeout=60)
        print("`figgy s3 find` passed.")
