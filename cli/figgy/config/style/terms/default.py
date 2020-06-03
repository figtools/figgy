from sty import fg

from figgy.config.style.color import Color
from figgy.config.style.palette import Palette
from figgy.config.style.terms.term import Term


class DefaultTerm(Term):
    TERM_PROGRAM = 'Unknown'
    BLUE = Palette.BLUE
    GREEN = Palette.GREEN
    RED = Palette.RED
    YELLOW = Palette.YELLOW

    def get_colors(self) -> Color:
        return Color(
            colors_enabled=self.colors_enabled,
            palette=Palette(
                blue=DefaultTerm.BLUE,
                green=DefaultTerm.GREEN,
                red=DefaultTerm.RED,
                yellow=DefaultTerm.YELLOW
            )
        )
