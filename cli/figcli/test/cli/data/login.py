import pexpect
from figcli.test.cli.config import *
from figcli.test.cli.figgy import FiggyTest
from figcli.config import *
from figcli.utils.utils import *
import os


class DataLogin(FiggyTest):

    def __init__(self, extra_args=""):
        super().__init__(pexpect.spawn(f'{CLI_NAME} login sandbox', timeout=10, encoding='utf-8'), extra_args=extra_args)

    def run(self):
        self.expect('.*user name:.*')
        self.sendline('FiggyDataTester')
        self.expect('.*weirdness.*')
        self.sendline('n')
        self.expect('.*Options.*devops.*')
        self.sendline('data')
        self.expect('.*default account.*')
        self.sendline('stage')
        self.expect('.*Login successful.*')
