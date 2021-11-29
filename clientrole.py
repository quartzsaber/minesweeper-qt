from abc import ABCMeta, abstractmethod
from typing import Optional, Callable, Sequence, Tuple

from constants import ImageType


class IClientRole(metaclass=ABCMeta):
    def __init__(self):
        self.rebuildCallback = lambda: None  # type: Callable[[], None]
        self.refreshCallback = lambda: None  # type: Callable[[], None]

    # 보드의 크기를 포함해서 모든 것을 새로고침하는 콜백
    def setRebuildCallback(self, fn: Callable[[], None]):
        self.rebuildCallback = fn

    # 셀들의 모습을 새로고침하는 콜백
    def setRefreshCallback(self, fn: Callable[[], None]):
        self.refreshCallback = fn

    @abstractmethod
    def cycleCellImage(self, x: int, y: int):
        pass

    @abstractmethod
    def openCell(self, x: int, y: int):
        pass

    @abstractmethod
    def openCellAdjacent(self, x: int, y: int):
        pass

    @abstractmethod
    def countRemainingMine(self) -> int:
        pass

    @abstractmethod
    def countMine(self) -> int:
        pass

    @abstractmethod
    def checkFinished(self) -> bool:
        pass

    @abstractmethod
    def getCellText(self, x: int, y: int) -> Optional[int]:
        pass

    @abstractmethod
    def getCellImage(self, x: int, y: int) -> ImageType:
        pass

    @abstractmethod
    def getPlaytime(self) -> float:
        pass

    @abstractmethod
    def height(self) -> int:
        pass

    @abstractmethod
    def width(self) -> int:
        pass
