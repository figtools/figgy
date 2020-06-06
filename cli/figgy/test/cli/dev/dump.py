import pexpect
import sys
from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *
from figgy.test.cli.dev.put import DevPut
from figgy.test.cli.dev.delete import DevDelete
import time


class DevDump(FiggyTest):

    def __init__(self):
        super().__init__(None)

    def run(self):
        put = DevPut()

        # Use a number > 10 so paging is tested
        minimum, maximum = 1, 12
        put.add(param_1, param_1_val, param_1_desc, add_more=True)

        for i in range(minimum, maximum):
            more = i < maximum - 1
            put.add_another(f'{param_1}-{i}', param_1_val, f'{param_1_desc}-{i}', add_more=more)

        child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(dump)} --env {DEFAULT_ENV} --skip-upgrade',
                              encoding='utf-8', timeout=7)

        self.step(f"Testing `{CLI_NAME} config {Utils.get_first(dump)} --env {DEFAULT_ENV}`")
        child.expect('.*to dump from.*')
        child.sendline(dump_prefix)
        child.expect(f'.*{param_1}-{minimum}.*{param_1}-{maximum-1}.*')
        print(f"Dump was successful.")

        delete = DevDelete()
        delete.delete(param_1, delete_another=True)
        for i in range(minimum, maximum):
            delete.delete(f'{param_1}-{i}', delete_another=i < maximum - 1)
