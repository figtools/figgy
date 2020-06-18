from abc import abstractmethod, ABC

from figcli.config.style.color import Color


class Term(ABC):
    TYPE = 'default'

    def __init__(self, colors_enabled: bool):
        self.colors_enabled = colors_enabled

    @abstractmethod
    def get_colors(self) -> Color:
        pass
