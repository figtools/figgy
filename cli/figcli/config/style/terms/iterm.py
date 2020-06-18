from sty import fg

from figcli.config.style.color import Color
from figcli.config.style.palette import Palette
from figcli.config.style.terms.term import Term


class iTerm(Term):
    TERM_PROGRAM = 'iTerm.app'
    BLUE = (52, 213, 235)
    GREEN = (51, 222, 136)
    RED = (240, 70, 87)
    YELLOW = (240, 240, 70)

    def get_colors(self) -> Color:
        return Color(
            colors_enabled=self.colors_enabled,
            palette=Palette(
                blue=iTerm.BLUE,
                green=iTerm.GREEN,
                red=iTerm.RED,
                yellow=iTerm.YELLOW
            )
        )
