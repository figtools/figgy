import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.data.put import *
from figgy.test.cli.data.delete import DataDelete
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *


class DataShare(FiggyTest):
    def __init__(self):
        print(f"Testing `{CLI_NAME} config {Utils.get_first(share)} --env {DEFAULT_ENV}`")
        super().__init__(None)
        self._child = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(share)} --env '
                                       f'{DEFAULT_ENV} --skip-upgrade', timeout=10, encoding='utf-8')

    def run(self):
        self.step("Adding parameters to share...")
        put = DataPut()
        put.add(data_param_1, data_param_1_val, data_param_1_desc, add_more=False)

        self.step(f"Testing share success from {figgy} to {automated_test_dest_1}")
        self.share(data_param_1, automated_test_dest_1, expect_failure=False, share_another=True)

        self.step("Testing share failure due to inaccessible namespace.")
        self.share(devops_param_1, automated_test_dest_1, expect_failure=True)

        delete = DataDelete()
        self.step("Testing failed deletion b/c source is a repl source.")
        delete.delete(data_param_1, delete_another=False, repl_source_delete=True)

        time.sleep(30)  # Wait for replication
        # print("Faking successful replication")
        # put.add(automated_test_dest_1, data_param_1_val, data_param_1_desc)

        delete = DataDelete()
        self.step("Testing successful deletion of a repl destination.")
        delete.delete(automated_test_dest_1, delete_another=False, repl_dest_delete=True)

    def share(self, source, destination, expect_failure=False, share_another=False):
        self.expect(".*Name you wish to share:.*")
        self.sendline(source)
        self.expect(".*destination of the shared value:.*")
        self.sendline(destination)

        if expect_failure:
            self.expect(".*ERROR:.*")
        else:
            self.expect(f".*{source}.*successfully shared.*Share another.*")
            if share_another:
                self.sendline('y')
            else:
                self.sendline('n')

