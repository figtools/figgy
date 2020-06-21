import pexpect
from figcli.test.cli.config import *
from figcli.test.cli.figgy import FiggyTest
from figcli.config import *
from figcli.utils.utils import *
import os


class DevLogin(FiggyTest):

    def __init__(self, extra_args="", env: str = DEFAULT_ENV):
        super().__init__(pexpect.spawn(f'{CLI_NAME} login sandbox', timeout=10, encoding='utf-8'),
                         extra_args=extra_args)
        self.env = env

    def run(self):
        self.expect('.*user name:.*')
        self.sendline('Figgy Dev Tester')
        self.expect('.*weirdness.*')
        self.sendline('n')
        self.expect('.*Options.*devops.*')
        self.sendline('dev')
        self.expect('.*default account.*')
        self.sendline(self.env)
        self.expect('.*Login successful.*')