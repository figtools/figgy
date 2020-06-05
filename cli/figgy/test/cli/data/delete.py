import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.dev.get import *
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *


class DataDelete(FiggyTest):
    def __init__(self):
        print(f"Testing `{CLI_NAME} config {Utils.get_first(delete)} --env {DEFAULT_ENV}`")
        super().__init__(pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(delete)} --env {DEFAULT_ENV} --skip-upgrade',
                                    timeout=5, encoding='utf-8'))

    def run(self):
        self.step(f"Testing delete for param: {param_1}")
        self.delete(param_1)

    def delete(self, name, delete_another=False, repl_source_delete=False, repl_dest_delete=False):
        self.expect('.*PS Name.*')
        self.sendline(name)
        print(f"Delete sent for {name}")
        if repl_source_delete:
            self.expect(".*You may NOT delete sources that are actively replicating.*")
        elif repl_dest_delete:
            match = self.expect_multiple([f".*active replication destination.*{name}.*", ".*deleted successfully.*"])
            print(f"Match: {match}")
            if match == 0:
                print("Matched replication destination message")
                self.sendline('y')
                self.expect(f".*{name}.*deleted successfully.*Delete another.*")
            else:
                print("Matched delete successful message")
        else:
            self.expect(f'.*deleted successfully.*Delete another.*')
            print("Validating delete success.")
            get = DevGet()
            get.get(param_1, param_1_val, expect_missing=True)

        if delete_another:
            self.sendline('y')
        else:
            self.sendline('n')

        print("Successful delete validated.")

