from sty import fg

from config.style.color import Color
from config.style.palette import Palette
from config.style.terms.term import Term


class DefaultTerm(Term):
    TERM_PROGRAM = 'Unknown'
    FG_BL = fg(33)
    FG_GR = fg(2)
    FG_RD = fg(160)
    FG_YL = fg(177)
    rs = fg.rs

    def get_colors(self) -> Color:
        return Color(
            colors_enabled=self.colors_enabled,
            palette=Palette(
                fg_bl=DefaultTerm.FG_BL,
                fg_gr=DefaultTerm.FG_GR,
                fg_rd=DefaultTerm.FG_RD,
                fg_yl=DefaultTerm.FG_YL
            )
        )
