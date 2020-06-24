import pexpect
from figcli.test.cli.config import *
from figcli.test.cli.figgy import FiggyTest
from figcli.utils.utils import *
import os


class ConfigureOkta(FiggyTest):
    def __init__(self, role_type: str):
        self._role_type = role_type
        super().__init__(pexpect.spawn(f'{CLI_NAME} --{Utils.get_first(configure)} --skip-upgrade',
                                       encoding='utf-8', timeout=10))
        # self._child = pexpect.spawn()

    def run(self):
        self.step(f"Testing `{CLI_NAME} --{Utils.get_first(configure)}`")
        user_name = os.environ.get(OKTA_SSO_USER)
        password = os.environ.get(OKTA_SSO_PASSWORD)
        embed_url = os.environ.get(OKTA_EMBED_URL)
        mfa_secret = os.environ.get(OKTA_MFA_SECRET)

        self._child.expect('.*select.*OKTA.*')
        self._child.sendline('OKTA')
        self._child.expect('.*OKTA username.*')
        self._child.sendline(user_name)
        self._child.expect('.*OKTA password.*')
        self._child.sendline(password)
        self._child.expect('.*mfa_enabled.*')
        self._child.sendline('n')
        self._child.expect('.*Use Multi-factor.*')
        self._child.sendline('y')
        self._child.expect('.*auto_mfa.*')
        self._child.sendline('n')
        self._child.expect('.*Would you.*generate.*')
        self._child.sendline('y')
        self._child.expect('.*auto-generate.*')
        self._child.sendline(mfa_secret)
        self._child.expect('.*app_link.*')
        self._child.sendline('n')
        self._child.expect('.*Embed Link.*')
        self._child.sendline(embed_url)
        self._child.expect('.*GOOGLE.*')
        self._child.sendline('y')
        self._child.expect('.*Options are.*')
        self._child.sendline(self._role_type)
        self._child.expect('.*Options.*dev.*')
        self._child.sendline('dev')
        self._child.expect('.*region.*')
        self._child.sendline('y')
        self._child.expect('.*colors.*')
        self._child.sendline('n')
        self._child.expect('.*weirdness.*')
        self._child.sendline('n')
        self._child.expect('.*overwrite.*')
        self._child.expect('.*Setup successful.*')
        self.step(f"OKTA with role: {self._role_type} configured successfully")
