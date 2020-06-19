from abc import ABC, abstractmethod
from typing import List

from pexpect.exceptions import TIMEOUT
from figcli.utils.utils import Utils
import sys


class FiggyTest(ABC):

    def __init__(self, child, extra_args=""):
        self.c = Utils.default_colors()
        self.extra_args = extra_args

        if child:
            c = Utils.default_colors()
            print(f"{c.fg_yl}Testing command: {child.args}{c.rs}")
            self._child = child
            self._child.logfile = sys.stdout

    @abstractmethod
    def run(self):
        pass

    def expect_multiple(self, regexes: List[str]):
        print(f'Expecting: {regexes}')
        return self._child.expect(regexes)

    def expect(self, regex: str):
        print(f'Expecting: {regex}')
        self._child.expect(regex)

    def sendline(self, line: str):
        print(f'Sending: {line}')
        self._child.sendline(line)

    def step(self, step_msg: str):
        print(f"{self.c.fg_bl}-----------------------------------------{self.c.rs}")
        print(f"{self.c.fg_yl} STEP: {step_msg}{self.c.rs}")
        print(f"{self.c.fg_bl}-----------------------------------------{self.c.rs}")