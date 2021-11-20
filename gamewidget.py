from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame, QGridLayout

from gameboard import GameBoard
from cellwidget import CellWidget


class GameWidget(QFrame):
    refreshBoard = pyqtSignal()

    def __init__(self, width: int, height: int, mines: int):
        super(QFrame, self).__init__()
        self.setFrameShadow(QFrame.Panel | QFrame.Sunken)

        self.board = GameBoard()
        self.board.newGame(width, height, mines)

        self.cells = []
        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(2)
        for i in range(self.board.height()):
            self.cells.append([])
            for j in range(self.board.width()):
                self.cells[i].append(CellWidget(self, j, i))
                self.gridLayout.addWidget(self.cells[i][j], i, j)

        self.setLayout(self.gridLayout)

    def updateAll(self):
        for row in self.cells:
            for cell in row:
                cell.updateDisplay()
        self.refreshBoard.emit()

    def getCell(self, x, y):
        return self.cells[y][x]

    def height(self):
        return self.board.height()

    def width(self):
        return self.board.width()
