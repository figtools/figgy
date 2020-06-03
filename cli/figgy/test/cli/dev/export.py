
import pexpect
from figgy.test.cli.config import *
from figgy.test.cli.figgy import FiggyTest
from figgy.config import *
from figgy.utils.utils import *


class DevExport(FiggyTest):

    def __init__(self):
        self._child = pexpect.spawn(f'python figgy.py {Utils.get_first(iam)} {Utils.get_first(export)} '
                                    f'--env {dev} --skip-upgrade', timeout=5)
        self._child.delayafterread = .01
        self._child.delaybeforesend = .5

    def run(self):
        print(f"Testing GET for {param_1}")
        self.export()

    def export(self):
        print(f"Testing IAM export.")
        self._child.expect('.*Successfully updated.*')
        print("`figgy iam export` passed.")
