import pexpect
from test.cli.config import *
from test.cli.dev.get import *
from test.cli.figgy import FiggyTest
from config import *
from utils.utils import *


class DataDelete(FiggyTest):
    def __init__(self):
        print(f"Testing `python figgy.py config {Utils.get_first(delete)} --env {dev}`")
        self._child = pexpect.spawn(f'python figgy.py config {Utils.get_first(delete)} --env {dev} --skip-upgrade', timeout=5)

    def run(self):
        self.delete(param_1)

    def delete(self, name, delete_another=False, repl_source_delete=False, repl_dest_delete=False):
        self._child.expect('.*PS Name to Delete.*')
        self._child.sendline(name)
        print(f"Delete sent for {name}")
        if repl_source_delete:
            self._child.expect(".*You may NOT delete sources that are actively replicating.*")
        elif repl_dest_delete:
            self._child.expect(f".*active replication destination.*{name}.*")
            self._child.sendline('y')
            self._child.expect(f".*{name}.*deleted successfully.*Delete another.*")
        else:
            self._child.expect(f'.*deleted successfully.*Delete another.*')
            print("Validating delete success.")
            get = DevGet()
            get.get(param_1, param_1_val, expect_missing=True)

        if delete_another:
            self._child.sendline('y')
        else:
            self._child.sendline('n')

        print("Successful delete validated.")

