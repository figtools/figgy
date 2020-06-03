import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.test.cli.dev.put import DevPut
from figgy.test.cli.dev.get import DevGet
from figgy.test.cli.dev.delete import DevDelete
from figgy.config import *
from figgy.utils.utils import *
import time

KEY_UP = 'k'
KEY_DOWN = 'j'
KEY_PATH = '/shared/aaa/aa'
class DevBrowse(FiggyTest):

    def run(self):
        print(f"Testing browse for {param_1}")
        self.browse()

    def _cleanup(self):
        delete = DevDelete()
        delete.delete(KEY_PATH, delete_another=False)

    def _setup(self):
        put = DevPut()
        put.add(KEY_PATH, DELETE_ME_VALUE, param_1_desc, add_more=False)

    def _validate_delete(self, key, value):
        print(f"Validating successfully deletion of {key}")
        get = DevGet()
        get.get(key, value, get_more=False, expect_missing=True)
        print("Delete success validated.")

    ## GEt through browse, then delete
    def browse(self):
        self._setup()
        print("Sleeping for 120s to ensure the cache gets populated with the new /shared value")
        time.sleep(120)
        print(f"Adding {KEY_PATH} through browse...")
        # Get Value
        child = pexpect.spawn(f'python figgy.py config {Utils.get_first(browse)} --env {dev} --skip-upgrade',
                                    timeout=10)
        child.sendline(KEY_DOWN)
        child.sendline('e')
        child.sendline(KEY_DOWN)
        child.sendline('e')
        child.sendline(KEY_DOWN)
        child.sendline('s')
        child.sendcontrol('n')  # <-- sends TAB
        child.sendcontrol('m')  # <-- Sends ENTER
        child.expect(f'.*{DELETE_ME_VALUE}.*')

        print("Add success. Deleting through browse.")
        # Delete Value
        child = pexpect.spawn(f'python figgy.py config {Utils.get_first(browse)} --env {dev} --skip-upgrade',
                                    timeout=10)
        child.sendline(KEY_DOWN)
        child.sendline('e')
        child.sendline(KEY_DOWN)
        child.sendline('e')
        child.sendline(KEY_DOWN)
        child.sendline('d')
        child.sendcontrol('n')  # <-- sends TAB
        child.sendcontrol('m')  # <-- Sends ENTER
        child.expect(f'.*{KEY_PATH}.*')
        child.sendline('y')
        child.expect(f'.*{KEY_PATH}.*deleted successfully.*')

        print("Delete success!")
        self._validate_delete(KEY_PATH, DELETE_ME_VALUE)