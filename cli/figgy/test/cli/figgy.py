from abc import ABC, abstractmethod


class FiggyTest(ABC):

    @abstractmethod
    def run(self):
        pass
