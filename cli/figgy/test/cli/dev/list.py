import sys

import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *
from figgy.test.cli.dev.put import DevPut
from figgy.test.cli.dev.delete import DevDelete
import time

class DevList(FiggyTest):

    def __init__(self):
        super().__init__(None)

    def run(self):
        # self.successful_list()
        self.test_empty_input()

    def test_empty_input(self):
        self.step("Testing empty input for list.")
        self._setup(1, 3)
        print(f"Testing {CLI_NAME} config {Utils.get_first(list_com)} --env dev")
        print("Waiting for cache population.")
        time.sleep(3)
        child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(list_com)} --env {DEFAULT_ENV} --skip-upgrade',
                              timeout=7, encoding='utf-8')
        child.expect('.*Please input a namespace prefix.*')
        child.sendline("")
        child.expect('.*Please input a namespace prefix.*')
        child.sendline("")
        child.expect('.*Please input a namespace prefix.*')
        child.sendline(dump_prefix)
        child.expect(f'.*1.*{dump_prefix}.*2.*{dump_prefix}.*3.*{param_1}.*Selection.*')
        child.sendline('3')
        child.expect(f'.*Value.*{param_1_val}.*')
        child.sendline('')
        child.sendline('3')
        child.sendline('')
        print("List successful. Cleaning up.")

        self._cleanup(1, 3)

    def successful_list(self):
        self._setup(1, 3)
        self.step("Testing successful list.")
        print(f"Testing {CLI_NAME} config {Utils.get_first(list_com)} --env dev")
        child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(list_com)} --env {DEFAULT_ENV} --skip-upgrade',
                              timeout=7, encoding='utf-8')

        print("Waiting for cache population.")
        time.sleep(15)
        child.expect('.*Please input a namespace prefix.*')
        child.sendline(dump_prefix)
        child.expect(f'.*1.*{dump_prefix}.*2.*{dump_prefix}.*3.*{param_1}.*Selection.*')
        child.sendline('3')
        child.expect(f'.*Value.*{param_1_val}.*')
        child.sendline('')
        child.sendline('3')
        child.sendline('')
        print("List successful. Cleaning up.")

        self._cleanup(1, 3)

    def _setup(self, min: int, max: int):
        put = DevPut()
        put.add(param_1, param_1_val, param_1_desc, add_more=True)
        for i in range(min, max):
            more = i < max - 1
            put.add_another(f'{param_1}-{i}', param_1_val, f'{param_1_desc}-{i}', add_more=more)


    def _cleanup(self, min: int, max: int):
        delete = DevDelete()
        delete.delete(param_1, delete_another=True)
        for i in range(min, max):
            delete.delete(f'{param_1}-{i}', delete_another=i < max - 1)

