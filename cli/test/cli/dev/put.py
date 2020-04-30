import pexpect
from test.cli.config import *
from test.cli.figgy import FiggyTest
from config import *
from utils.utils import *


class DevPut(FiggyTest):
    def __init__(self):
        print(f"Testing `figgy config {Utils.get_first(put)} --env {dev}`")
        self._child = pexpect.spawn(f'python figgy.py config {Utils.get_first(put)} --env {dev} --skip-upgrade', timeout=7)

    def run(self):
        print(f"Testing PUT for {param_1}")
        self.add(param_1, param_1_val, param_1_desc)

    def add(self, key, value, desc, add_more=False):
        print(f"Adding: {key} -> {value}")
        self._child.expect('.*Please input a PS Name.*')
        self._child.sendline(key)
        self._child.expect('.*Please input a value.*')
        self._child.sendline(value)
        self._child.expect('.*Please input an optional.*')
        self._child.sendline(desc)
        self._child.expect('.*Add another.*')
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
        self._child.expect('.*Add another.*')
        if add_more:
            self._child.sendline('y')
        else:
            self._child.sendline('n')
