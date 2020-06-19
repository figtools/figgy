
import pexpect
from figcli.test.cli.config import *
from figcli.test.cli.figgy import FiggyTest
from figcli.config import *
from figcli.utils.utils import *


class DevExport(FiggyTest):

    def __init__(self, extra_args=""):
        super().__init__(pexpect.spawn(f'{CLI_NAME} {Utils.get_first(iam)} {Utils.get_first(export)} '
                                    f'--env {DEFAULT_ENV} --skip-upgrade {extra_args}', timeout=5, encoding='utf-8'),
                                    extra_args=extra_args)
        self._child.delayafterread = .01
        self._child.delaybeforesend = .5

    def run(self):
        self.step("Testing IAM export.")
        self.export()

    def export(self):
        print(f"Testing IAM export.")
        self.expect('.*Successfully updated.*')
        print("`figgy iam export` passed.")
