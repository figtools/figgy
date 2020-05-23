from prompt_toolkit.styles import Style
from sty import fg

# Prompt Colors
style = Style.from_dict({
    # Prompt.
    'blue': '#00afff',
    'green': '#008000',
    'red': '#d70000'
})


class Color:
    # Static colors
    bl = 'blue'
    gr = 'green'
    rd = 'red'

    fg_bl = fg(33)
    fg_gr = fg(2)
    fg_rd = fg(160)
    rs = fg.rs

    def __init__(self, colors_enabled):
        self.bl, self.gr, self.rd, self.fg_bl, self.fg_gr, self.fg_rd, self.rs = '', '', '', '', '', '', ''
        if colors_enabled:
            self.bl = Color.bl
            self.gr = Color.gr
            self.rd = Color.rd
            self.fg_bl = Color.fg_bl
            self.fg_gr = Color.fg_gr
            self.fg_rd = Color.fg_rd
            self.rs = fg.rs
