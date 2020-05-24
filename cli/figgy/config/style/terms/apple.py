from sty import fg

from config.style.color import Color
from config.style.palette import Palette
from config.style.terms.term import Term


class AppleTerminal(Term):
    TERM_PROGRAM = 'Apple_Terminal'
    FG_BL = fg(33)
    FG_GR = fg(2)
    FG_RD = fg(160)
    FG_YL = fg(177)
    rs = fg.rs

    def get_colors(self) -> Color:
        return Color(
            colors_enabled=self.colors_enabled,
            palette=Palette(
                fg_bl=AppleTerminal.FG_BL,
                fg_gr=AppleTerminal.FG_GR,
                fg_rd=AppleTerminal.FG_RD,
                fg_yl=AppleTerminal.FG_YL
            )
        )
