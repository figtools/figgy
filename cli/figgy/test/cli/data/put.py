import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *


class DataPut(FiggyTest):
    def __init__(self):
        print(f"Testing `python figgy.py config {Utils.get_first(put)} --env {dev}`")
        self._child = pexpect.spawn(f'python figgy.py config {Utils.get_first(put)} --env {dev} --skip-upgrade', timeout=7)

    def run(self):
        self._child.expect('.*Please input a PS Name.*')
        self._child.sendline(data_param_1)
        self._child.expect('.*Please input a value.*')
        self._child.sendline(data_param_1_val)
        self._child.expect('.*Please input an optional.*')
        self._child.sendline(data_param_1_desc)
        self._child.expect('.*Add another?.*')
        self._child.sendline('n')

    def add(self, key, value, desc, add_more=False):
        print(f"Adding: {key} -> {value}")
        self._child.expect('.*Please input a PS Name.*')
        self._child.sendline(key)
        self._child.expect('.*Please input a value.*')
        self._child.sendline(value)
        self._child.expect('.*Please input an optional.*')
        self._child.sendline(desc)
        self._child.expect('.*Is this value a secret.*')
        self._child.sendline('y')
        self._child.expect('.*Add another?.*')
        if add_more:
            self._child.sendline('y')
        else:
            self._child.sendline('n')

    def add_another(self, key, value, desc, add_more=True):
        print(f"Adding another: {key} -> {value}")
        self._child.expect('.*Please input a PS Name.*')
        self._child.sendline(key)
        self._child.expect('.*Please input a value.*')
        self._child.sendline(value)
        self._child.expect('.*Please input an optional.*')
        self._child.sendline(desc)
        self._child.expect('.*Add another?.*')
        if add_more:
            self._child.sendline('y')
        else:
            self._child.sendline('n')