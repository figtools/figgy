from sty import fg

from figcli.config.style.palette import Palette


class Color:
    def __init__(self, colors_enabled: bool, palette=Palette()):
        self.bl, self.gr, self.rd, self.fg_bl, self.fg_gr, self.fg_rd, self.rs = '', '', '', '', '', '', ''
        self.yl, self.fg_yl, self.bl_val, self.gr_val, self.yl_val, self.rd_val = '', '', '', '', '', ''
        if colors_enabled:
            self.bl = 'blue'
            self.rd = 'red'
            self.yl = 'yellow'
            self.gr = 'green'

            self.bl_val = palette.bl
            self.gr_val = palette.gr
            self.rd_val = palette.rd
            self.yl_val = palette.yl

            self.fg_bl = palette.fg_bl
            self.fg_gr = palette.fg_gr
            self.fg_rd = palette.fg_rd
            self.fg_yl = palette.fg_yl
            self.rs = fg.rs
