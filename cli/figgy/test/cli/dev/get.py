import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *


class DevGet(FiggyTest):

    def __init__(self):
        self._child = pexpect.spawn(f'python figgy.py config {Utils.get_first(get)} --env {dev} --skip-upgrade',
                                    timeout=5)
        self._child.delayafterread = .01
        self._child.delaybeforesend = .5

    def run(self):
        print(f"Testing GET for {param_1}")
        self.get(param_1, param_1_val, get_more=False)

    def get(self, key, value, get_more=False, expect_missing=False):
        print(f"Getting key: {key} with more: {get_more}")
        self._child.expect('.*Please input.*')
        self._child.sendline(key)
        if expect_missing:
            self._child.expect(f'.*Invalid PS Name specified..*')
            print("Missing parameter validated.")
        else:
            self._child.expect(f'.*{value}.*Get another.*')
            print(f"Expected value of {value} validated.")
        if get_more:
            print("Getting another")
            self._child.sendline('y')
        else:
            print("Not getting another")
            self._child.sendline('n')
