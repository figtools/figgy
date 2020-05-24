from sty import fg

from config.style.color import Color
from config.style.palette import Palette
from config.style.terms.term import Term


class iTerm(Term):
    TERM_PROGRAM = 'iTerm.app'
    FG_BL = fg(52, 213, 235)
    FG_GR = fg(51, 222, 136)
    FG_RD = fg(240, 70, 87)
    FG_YL = fg(240, 240, 70)

    def get_colors(self) -> Color:
        return Color(
            colors_enabled=self.colors_enabled,
            palette=Palette(
                fg_bl=iTerm.FG_BL,
                fg_gr=iTerm.FG_GR,
                fg_rd=iTerm.FG_RD,
                fg_yl=iTerm.FG_YL
            )
        )
