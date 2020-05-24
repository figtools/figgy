from sty import fg

from config.style.palette import Palette


class Color:
    def __init__(self, colors_enabled, palette=Palette()):
        self.bl, self.gr, self.rd, self.fg_bl, self.fg_gr, self.fg_rd, self.rs = '', '', '', '', '', '', ''
        if colors_enabled:
            self.bl = palette.bl
            self.gr = palette.gr
            self.rd = palette.rd
            self.yl = palette.yl
            self.fg_bl = palette.fg_bl
            self.fg_gr = palette.fg_gr
            self.fg_rd = palette.fg_rd
            self.fg_yl = palette.fg_yl
            self.rs = fg.rs

