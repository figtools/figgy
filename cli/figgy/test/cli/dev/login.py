import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *
import os


class DevLogin(FiggyTest):

    def __init__(self):
        super().__init__(pexpect.spawn(f'{CLI_NAME} login sandbox', timeout=10, encoding='utf-8'))

    def run(self):
        self.expect('.*user name:.*')
        self.sendline('Figgy Dev Tester')
        self.expect('.*Options.*devops.*')
        self.sendline('dev')
        self.expect('.*weirdness.*')
        self.sendline('n')
        self.expect('.*default account.*')
        self.sendline(DEFAULT_ENV)
        self.expect('.*Login successful.*')
