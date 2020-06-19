import sys

import pexpect
from figcli.test.cli.config import *
from figcli.test.cli.figgy import FiggyTest
from figcli.test.cli.dev.put import DevPut
from figcli.test.cli.dev.get import DevGet
from figcli.test.cli.dev.delete import DevDelete
from figcli.config import *
from figcli.utils.utils import *
import time


#Todo get this working...
class DevEdit(FiggyTest):
    _VALUE = 'asdf'
    _DESC = 'desc'

    def __init__(self, extra_args=""):
        super().__init__(None, extra_args=extra_args)

    def run(self):
        self.step(f"Testing edit for {param_1}")
        self.edit()

    def edit(self):
        # Get Value
        child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(edit)} --env {DEFAULT_ENV} '
                              f'--skip-upgrade {self.extra_args}',
                              timeout=10, encoding='utf-8')

        child.expect('.*Please input a PS Name.*')
        child.sendline(param_1)
        time.sleep(3) # Give edit time to start
        child.send(DevEdit._VALUE)
        child.sendcontrol('n')  # <-- sends TAB
        child.send(DevEdit._DESC)
        child.sendcontrol('n')  # <-- sends TAB
        child.sendcontrol('m')  # <-- Sends ENTER
        child.expect('.*secret.*')
        child.sendline('n')
        print("Add success. Checking successful save")

        get = DevGet(extra_args=self.extra_args)
        get.get(param_1, DevEdit._VALUE, DevEdit._DESC)
        delete = DevDelete(extra_args=self.extra_args)
        delete.delete(param_1)
