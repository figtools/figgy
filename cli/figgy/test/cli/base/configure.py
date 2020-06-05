import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *


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
