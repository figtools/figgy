import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *
import os


class DataLogin(FiggyTest):

    def __init__(self):
        super().__init__(pexpect.spawn(f'{CLI_NAME} login sandbox', timeout=10, encoding='utf-8'))

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
