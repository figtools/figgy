import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.data.put import *
from figgy.test.cli.data.delete import DataDelete
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *


class DataShare(FiggyTest):
    def __init__(self):
        print(f"Testing `python figgy.py config {Utils.get_first(share)} --env {dev}`")
        self._child = pexpect.spawn(f'python figgy.py config {Utils.get_first(share)} --env {dev} --skip-upgrade', timeout=10)

    def run(self):
        put = DataPut()
        put.add(data_param_1, data_param_1_val, data_param_1_desc, add_more=False)

        print(f"Testing share success from {data_param_1} to {automated_test_dest_1}")
        self.share(data_param_1, automated_test_dest_1, expect_failure=False, share_another=True)
        print("Testing share failure due to inaccessible namespace.")
        self.share(devops_param_1, automated_test_dest_1, expect_failure=True)

        delete = DataDelete()
        print("Testing failed deletion b/c source is a repl source.")
        delete.delete(data_param_1, delete_another=False, repl_source_delete=True)

        print("Faking successful replication")
        put = DataPut()
        put.add(automated_test_dest_1, data_param_1_val, data_param_1_desc)

        delete = DataDelete()
        print("Testing successful deletion of a repl destination.")
        delete.delete(automated_test_dest_1, delete_another=False, repl_dest_delete=True)

    def share(self, source, destination, expect_failure=False, share_another=False):
        self._child.expect(".*Name you wish to share:.*")
        self._child.sendline(source)
        self._child.expect(".*destination of the shared value:.*")
        self._child.sendline(destination)

        if expect_failure:
            self._child.expect(".*ERROR:.*")
        else:
            self._child.expect(f".*{source}.*successfully shared.*Share another.*")
            if share_another:
                self._child.sendline('y')
            else:
                self._child.sendline('n')


