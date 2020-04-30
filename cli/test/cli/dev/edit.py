import pexpect
from test.cli.config import *
from test.cli.figgy import FiggyTest
from test.cli.dev.put import DevPut
from test.cli.dev.get import DevGet
from test.cli.dev.delete import DevDelete
from config import *
from utils.utils import *
import time


#Todo get this working...
class DevEdit(FiggyTest):
    _VALUE = 'asdf'
    _DESC = 'desc'

    def run(self):
        print(f"Testing edit for {param_1}")
        self.edit()

    def edit(self):
        # Get Value
        child = pexpect.spawn(f'python figgy.py config {Utils.get_first(edit)} --env {dev} --skip-upgrade',
                              timeout=10)
        child.delayafterread = .01
        child.delaybeforesend = .5

        child.expect('.*Please input a PS Name.*')
        child.sendline(param_1)
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
        delete.delete()
