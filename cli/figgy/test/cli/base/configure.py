import pexpect
from test.cli.config import *
from test.cli.figgy import FiggyTest
from config import *
from utils.utils import *


class Configure(FiggyTest):
    def __init__(self, **kwargs):
        self.role = kwargs["role"]
        self.run()

    def run(self):
        child = pexpect.spawn(f'figgy --{Utils.get_first(configure)}', timeout=3)
        child.expect('.*Please input.*')
        child.sendline('bastion')
        child.expect('.*What type of user.*')
        child.sendline(self.role)
        child.expect('.*Enable.* colored output.*')
        child.sendline('n')
        child.expect('.*figgy successfully configured..*')
