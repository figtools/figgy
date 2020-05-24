from config import Color
from models.defaults.defaults import CLIDefaults


class FiggyVersionTracker:

    def __init__(self, cli_defaults: CLIDefaults):
        self._cli_defaults = cli_defaults
        self.c = TerminalFactory(self._cli_defaults.colors_enabled).instance().get_colors()

    def check_version(self):
        pass

    def push_version(self):
        pass
