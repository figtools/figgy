import pexpect
from test.cli.config import *
from test.cli.dev.get import DevGet
from test.cli.figgy import FiggyTest
from config import *
from utils.utils import *


class DevDelete(FiggyTest):
    def __init__(self):
        print(f"Testing `figgy config {Utils.get_first(delete)} --env {dev}`")
        self._child = pexpect.spawn(f'python figgy.py config {Utils.get_first(delete)} --env {dev} --skip-upgrade', timeout=5)
        self._child.delayafterread = .01
        self._child.delaybeforesend = .5
    def run(self):
        print(f"Testing DELETE for {param_1}")
        self.delete(param_1)

    def delete(self, name, delete_another=False):
        self._child.expect('.*PS Name to Delete.*')
        self._child.sendline(name)
        print(f"Delete sent for {name}")
        self._child.expect(f'.*deleted successfully.*Delete another.*')

        print("Validating delete success.")
        get = DevGet()
        get.get(name, DELETE_ME_VALUE, expect_missing=True)

        if delete_another:
            self._child.sendline('y')
        else:
            self._child.sendline('n')

        print("Successful delete validated.")

