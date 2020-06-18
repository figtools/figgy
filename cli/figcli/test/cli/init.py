import pexpect
from figcli.test.cli.config import *
from figcli.test.cli.figgy import FiggyTest
from figcli.config import *
from figcli.utils.utils import *
from subprocess import check_output
from figcli.test.cli.dev.configure import DevConfigure
from figcli.test.cli.data.configure import DataConfigure
from figcli.test.cli.devops.configure import DevOpsConfigure
import time

class CLIInit:

    @staticmethod
    def init(role: str):
        assert role in user_types
        if role == usr_dev:
            DevConfigure().run()
        elif role == usr_data:
            DataConfigure().run()
        elif role == usr_devops:
            DevOpsConfigure().run()

        figgy = pexpect.spawn(f'{CLI_NAME} config {Utils.get_first(get)} --env {DEFAULT_ENV} --prompt --skip-upgrade',
                                    timeout=5, encoding='utf-8')
        figgy.expect('.*Please input the MFA.*')
        mfa = check_output(["mfa", "otp", os.environ[MFA_USER_ENV_KEY]])
        mfa = str(mfa, 'utf-8').rstrip()
        print(f"Sending mfa {mfa}")
        figgy.sendline(mfa)
        figgy.expect('.*What type.*')
        figgy.sendline(role)
        result = figgy.expect(['.*input a PS Name.*', '.*Invalid MFA code.*'])
        count = 0
        # If mfa is invalid, keep trying.
        while result == 1 and count < 15:
            count = count + 1
            mfa = check_output(["mfa", "otp", os.environ[MFA_USER_ENV_KEY]])
            mfa = str(mfa, 'utf-8').rstrip()
            print(f"Retrying MFA: {mfa} - Attempt # {count}")
            figgy.sendline(mfa)
            result = figgy.expect(['.*input a PS Name.*', '.*Invalid MFA code.*'])
            time.sleep(10)

        time.sleep(15)


