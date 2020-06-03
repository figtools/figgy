import pexpect

from figgy.test.cli.figgy import FiggyTest
from figgy.utils.utils import *


class DevRunTests(FiggyTest):

    def __init__(self):
        self._child = pexpect.spawn(f'python figgy.py {Utils.get_first(cicd)} {Utils.get_first(run_tests)} '
                                    f'--env {dev} --skip-upgrade', timeout=5)
        self._child.delayafterread = .01
        self._child.delaybeforesend = .5

    def run(self):
        self.run_tests()

    def run_tests(self):
        print(f"Testing cicd run_tests")
        self._child.expect('.*service to trigger.*', timeout=15)
        self._child.sendline('jobs')
        self._child.expect('.*Tests successfully kicked.*', timeout=10)
        print("`figgy cicd run-tests` passed.")
