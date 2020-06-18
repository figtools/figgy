import pexpect
from figcli.test.cli.config import *
from figcli.test.cli.figgy import FiggyTest
from figcli.config import *
from figcli.utils.utils import *


class Configure(FiggyTest):
    def __init__(self, **kwargs):
        self.role = kwargs["role"]
        self.run()

    def run(self):
        child = pexpect.spawn(f'figgy --{Utils.get_first(configure)}', timeout=3, encoding='utf-8')
        child.expect('.*Please input.*')
        child.sendline('bastion')
        child.expect('.*What type of user.*')
        child.sendline(self.role)
        child.expect('.*Enable.* colored output.*')
        child.sendline('n')
        child.expect('.*figgy successfully configured..*')
