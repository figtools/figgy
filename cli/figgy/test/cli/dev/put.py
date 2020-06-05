import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *
import sys


class DevPut(FiggyTest):
    def __init__(self):
        print(f"Testing `figgy config {Utils.get_first(put)} --env {DEFAULT_ENV}`")
        super().__init__(pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(put)} '
                                    f'--env {DEFAULT_ENV} --skip-upgrade', timeout=7, encoding='utf-8'))

    def run(self):
        self.step(f"Testing PUT for {param_1}")
        self.add(param_1, param_1_val, param_1_desc)

    def add(self, key, value, desc, add_more=False):
        self.expect('.*Please input a PS Name.*')
        self.sendline(key)
        self.expect('.*Please input a value.*')
        self.sendline(value)
        self.expect('.*Please input an optional.*')
        self.sendline(desc)
        self.expect('.*secret?.*')
        self.sendline('n')
        self.expect('.*another.*')
        if add_more:
            self.sendline('y')
        else:
            self.sendline('n')

    def add_another(self, key, value, desc, add_more=True):
        print(f"Adding another: {key} -> {value}")
        self.expect('.*PS Name.*')
        self.sendline(key)
        self.expect('.*Please input a value.*')
        self.sendline(value)
        self.expect('.*Please input an optional.*')
        self.sendline(desc)
        self.expect('.*secret?.*')
        self.sendline('n')
        self.expect('.*Add another.*')
        if add_more:
            self.sendline('y')
        else:
            self.sendline('n')
