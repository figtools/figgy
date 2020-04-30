
import pexpect
from test.cli.config import *
from test.cli.figgy import FiggyTest
from config import *
from utils.utils import *


class DevAuth(FiggyTest):

    def __init__(self):
        self._child = pexpect.spawn(f'python figgy.py {Utils.get_first(tfe)} {Utils.get_first(auth)} '
                                    f'--skip-upgrade', timeout=5)
        self._child.delayafterread = .01
        self._child.delaybeforesend = .5

    def run(self):
        self.auth()

    def auth(self):
        print(f"Testing `figgy tfe auth`")
        self._child.expect('.*Please select a workspace.*')
        self._child.sendline('development-support')
        self._child.expect('.*Credentials successfully pushed to TFE Workspace.*', timeout=15)
        print("`figgy tfe auth` passed.")
