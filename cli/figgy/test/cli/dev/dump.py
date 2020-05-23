import pexpect
from test.cli.config import *
from test.cli.figgy import FiggyTest
from config import *
from utils.utils import *
from test.cli.dev.put import DevPut
from test.cli.dev.delete import DevDelete
import time


class DevDump(FiggyTest):

    def run(self):
        put = DevPut()

        # Use a number > 10 so paging is tested
        minimum, maximum = 1, 12
        put.add(param_1, param_1_val, param_1_desc, add_more=True)
        for i in range(minimum, maximum):
            more = i < maximum - 1
            put.add_another(f'{param_1}-{i}', param_1_val, f'{param_1_desc}-{i}', add_more=more)

        child = pexpect.spawn(f'python figgy.py config {Utils.get_first(dump)} --env {dev} --skip-upgrade', timeout=7)
        print(f"Testing `python figgy.py config {Utils.get_first(dump)} --env {dev}`")
        child.expect('.*to dump from.*')
        child.sendline(dump_prefix)
        child.expect(f'.*{param_1}-{minimum}.*{param_1}-{maximum-1}.*')
        print(f"Dump was successful.")

        delete = DevDelete()
        delete.delete(param_1, delete_another=True)
        for i in range(minimum, maximum):
            delete.delete(f'{param_1}-{i}', delete_another=i < maximum - 1)
