import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *
import os


class DevOpsConfigure(FiggyTest):

    def run(self):
        print(f"Testing `{CLI_NAME} --{Utils.get_first(configure)}`")
        child = pexpect.spawn(f'{CLI_NAME} --{Utils.get_first(configure)} --skip-upgrade',
                              encoding='utf-8', timeout=3)
        user_name = os.environ.get(SNAGBOT_USER_ENV_KEY)
        password = os.environ.get(SNAGBOT_PASSWORD_ENV_KEY)

        child.expect('.*What type of user.*')
        child.sendline('devops')
        child.expect('.*Enable.* colored output.*')
        child.sendline('n')
        child.expect('.*Please input OKTA username.*')
        child.sendline(user_name)
        child.expect('.*Please input OKTA password.*')
        child.sendline(password)
        child.expect('.*default account.*')
        child.sendline(dev)
        child.expect('.*figgy successfully configured..*')

