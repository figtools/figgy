from abc import ABC, abstractmethod


class Factory(ABC):

    @abstractmethod
    def instance(self):
        pass
