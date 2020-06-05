import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *


class DevGet(FiggyTest):

    def __init__(self):
        super().__init__(pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(get)} --env {DEFAULT_ENV} --skip-upgrade',
                                    timeout=10, encoding='utf-8'))
        self._child.delayafterread = .01
        self._child.delaybeforesend = .5

    def run(self):
        self.step(f"Testing GET for {param_1}")
        self.get(param_1, param_1_val, get_more=False)

    def get(self, key, value, get_more=False, expect_missing=False, no_decrypt=False):
        self.expect('.*PS Name*')
        self.sendline(key)
        if expect_missing:
            self.expect(f'.*Invalid PS Name specified..*')
            print("Missing parameter validated.")
        elif no_decrypt:
            self.expect(f'.*do not have access.*')
            print("Lack of decrypt permissions validated.")
        else:
            self.expect(f'.*{value}.*Get another.*')
            print(f"Expected value of {value} validated.")
        if get_more:
            print("Getting another")
            self.sendline('y')
        else:
            print("Not getting another")
            self.sendline('n')
