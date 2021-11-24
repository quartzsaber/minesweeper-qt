import time

from typing import Optional

from constants import ImageType
from gameboard import GameBoard
from serverrole import IServerRole
from clientrole import IClientRole


class IntegratedServer(IServerRole, IClientRole):
    def __init__(self):
        super().__init__()
        self.board = GameBoard()
        self.startTime = -1
        self.endTime = -1

    def newGame(self, width: int, height: int, mines: int):
        self.board.newGame(width, height, mines)
        self.startTime = -1
        self.endTime = -1
        self.rebuildCallback()

    def newGameSameConfig(self):
        self.board.newGame(self.width(), self.height(), self.board.countMine())
        self.startTime = -1
        self.endTime = -1
        self.refreshCallback()

    def cycleCellImage(self, x: int, y: int):
        if self.startTime < 0:
            self.startTime = time.monotonic()

        self.board.cycleCellImage(x, y)
        self.refreshCallback()

    def openCell(self, x: int, y: int):
        if self.startTime < 0:
            self.startTime = time.monotonic()

        if self.board.openCell(x, y):
            self.board.finishGame()
            self.endTime = time.monotonic()
        elif self.board.checkFinished():
            self.endTime = time.monotonic()

        self.refreshCallback()

    def openCellAdjacent(self, x: int, y: int):
        if self.startTime < 0:
            self.startTime = time.monotonic()

        if self.board.openCellAdjacent(x, y):
            self.board.finishGame()
            self.endTime = time.monotonic()
        elif self.board.checkFinished():
            self.endTime = time.monotonic()

        self.refreshCallback()

    def countRemainingMine(self) -> int:
        return self.board.countRemainingMine()

    def checkFinished(self) -> bool:
        return self.endTime >= 0

    def getCellText(self, x: int, y: int) -> Optional[int]:
        return self.board.getCellText(x, y)

    def getCellImage(self, x: int, y: int) -> ImageType:
        return self.board.getCellImage(x, y)

    def getPlaytime(self) -> float:
        if self.endTime >= 0:
            return self.endTime - self.startTime
        if self.startTime >= 0:
            return time.monotonic() - self.startTime
        return 0

    def height(self) -> int:
        return self.board.height()

    def width(self) -> int:
        return self.board.width()
