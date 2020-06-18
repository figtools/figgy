import os

from figcli.config.style.terms.default import DefaultTerm
from figcli.config.style.terms.iterm import iTerm
from figcli.config.style.terms.apple import AppleTerminal


class TerminalFactory:
    TRUE_COLOR = 'truecolor'

    def __init__(self, colors_enabled: bool):
        self.term = os.environ.get('TERM')
        self.term_program = os.environ.get('TERM_PROGRAM')
        self.color_term = os.environ.get('COLORTERM')
        self.colors_enabled = colors_enabled

    def instance(self):
        if self.term_program == iTerm.TERM_PROGRAM or self.color_term == 'truecolor':
            return iTerm(self.colors_enabled)
        elif self.term_program == AppleTerminal.TERM_PROGRAM:
            return AppleTerminal(self.colors_enabled)
        else:
            return DefaultTerm(self.colors_enabled)
