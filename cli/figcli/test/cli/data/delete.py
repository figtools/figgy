import pexpect
from figcli.test.cli.config import *
from figcli.test.cli.dev.get import *
from figcli.test.cli.figgy import FiggyTest
from figcli.config import *
from figcli.utils.utils import *


class DataDelete(FiggyTest):
    def __init__(self, extra_args=""):
        print(f"Testing `{CLI_NAME} config {Utils.get_first(delete)} --env {DEFAULT_ENV}`")
        super().__init__(pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(delete)} --env {DEFAULT_ENV}'
                                       f' --skip-upgrade {extra_args}',
                                    timeout=5, encoding='utf-8'), extra_args=extra_args)

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
            get = DevGet(extra_args=self.extra_args)
            get.get(param_1, param_1_val, expect_missing=True)

        if delete_another:
            self.sendline('y')
        else:
            self.sendline('n')

        print("Successful delete validated.")

