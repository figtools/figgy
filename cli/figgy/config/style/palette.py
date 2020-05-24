from dataclasses import dataclass
from sty import fg, FgRegister, Rule


@dataclass
class Palette:
    # Static colors
    bl: str = 'blue'
    gr: str = 'green'
    rd: str = 'red'
    yl:str = 'yellow'

    fg_bl: FgRegister = fg(52, 213, 235)
    fg_gr: FgRegister = fg(51, 222, 136)
    fg_rd: FgRegister = fg(240, 70, 87)
    fg_yl: FgRegister = fg(240, 240, 70)
    rs: Rule = fg.rs