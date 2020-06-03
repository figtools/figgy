import pexpect
from figgy.test.cli.base.configure import Configure
from figgy.utils.utils import *


class Restore:
    def __init__(self, **kwargs):
        self.env = kwargs["env"]
        self._child = pexpect.spawn(f'python3 figgy.py config {Utils.get_first(restore)} --env {self.env}', timeout=5)

    def choose_key(self, key: str, expect: str) -> None:
        self._child.expect("Please input.+: ")
        self._child.sendline(key)
        self._child.expect(expect)

    def choose_restore_item(self, item_choice: str, expect: str):
        self._child.sendline(item_choice)
        self._child.expect(expect)

    def confirm_restore_item(self, expect: str, confirm: str ='y'):
        self._child.sendline(confirm)
        self._child.expect(expect)

