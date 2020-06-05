import sys

import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.test.cli.dev.put import DevPut
from figgy.test.cli.dev.get import DevGet
from figgy.test.cli.dev.delete import DevDelete
from figgy.config import *
from figgy.utils.utils import *
import time


#Todo get this working...
class DevEdit(FiggyTest):
    _VALUE = 'asdf'
    _DESC = 'desc'

    def __init__(self):
        super().__init__(None)

    def run(self):
        self.step(f"Testing edit for {param_1}")
        self.edit()

    def edit(self):
        # Get Value
        child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(edit)} --env {DEFAULT_ENV} --skip-upgrade',
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

        get = DevGet()
        get.get(param_1, DevEdit._VALUE, DevEdit._DESC)
        delete = DevDelete()
        delete.delete(param_1)
