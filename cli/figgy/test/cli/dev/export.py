
import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *


class DevExport(FiggyTest):

    def __init__(self):
        super().__init__(pexpect.spawn(f'{CLI_NAME} {Utils.get_first(iam)} {Utils.get_first(export)} '
                                    f'--env {DEFAULT_ENV} --skip-upgrade', timeout=5, encoding='utf-8'))
        self._child.delayafterread = .01
        self._child.delaybeforesend = .5

    def run(self):
        self.step("Testing IAM export.")
        self.export()

    def export(self):
        print(f"Testing IAM export.")
        self.expect('.*Successfully updated.*')
        print("`figgy iam export` passed.")
