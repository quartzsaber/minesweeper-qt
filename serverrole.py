from abc import ABCMeta, abstractmethod


class IServerRole(metaclass=ABCMeta):
    @abstractmethod
    def newGame(self, width: int, height: int, mines: int):
        pass

    @abstractmethod
    def newGameSameConfig(self):
        pass
