import pexpect
from figcli.test.cli.base.configure import Configure
from figcli.utils.utils import *


class Restore:
    def __init__(self, **kwargs):
        self.env = kwargs["env"]
        super().__init__(pexpect.spawn(f'python3 {CLI_NAME} config {Utils.get_first(restore)} --env {self.env}',
                                       encoding='utf-8', timeout=5))

    def choose_key(self, key: str, expect: str) -> None:
        self.expect("Please input.+: ")
        self.sendline(key)
        self.expect(expect)

    def choose_restore_item(self, item_choice: str, expect: str):
        self.sendline(item_choice)
        self.expect(expect)

    def confirm_restore_item(self, expect: str, confirm: str ='y'):
        self.sendline(confirm)
        self.expect(expect)

