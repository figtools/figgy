import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *


class DataPut(FiggyTest):
    def __init__(self):
        super().__init__(pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(put)} --env {DEFAULT_ENV} --skip-upgrade',
                      timeout=7, encoding='utf-8'))
        self.step(f"Testing `{CLI_NAME} config {Utils.get_first(put)} --env {DEFAULT_ENV}`")

    def run(self):
        self.expect('.*Please input a PS Name.*')
        self.sendline(data_param_1)
        self.expect('.*Please input a value.*')
        self.sendline(data_param_1_val)
        self.expect('.*Please input an optional.*')
        self.sendline(data_param_1_desc)
        self.expect('.*secret?.*')
        self.sendline('n')
        self.expect('.*Add another?.*')
        self.sendline('y')
        self.expect('.*PS Name.*')
        self.sendline('/devops/test/invalid')
        self.expect('.*value.*')
        self.sendline(DELETE_ME_VALUE)
        self.expect('.*not have permissions.*another?.*')
        self.sendline('n')

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
