from typing import Optional

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QFrame, QGridLayout, QWidget

from cellwidget import CellWidget
from serverrole import IServerRole
from clientrole import IClientRole
from integratedserver import IntegratedServer


class GameWidget(QFrame):
    refreshed = pyqtSignal()
    rebuildLater = pyqtSignal()
    refreshLater = pyqtSignal()

    def __init__(self):
        super(QFrame, self).__init__()
        self.rebuildLater.connect(self.buildUi)
        self.refreshLater.connect(self.updateUi)

        self.setFrameShadow(QFrame.Panel | QFrame.Sunken)

        integratedServer = IntegratedServer()
        self.server = integratedServer  # type: Optional[IServerRole]
        self.client = integratedServer  # type: IClientRole

        self.server.newGame(9, 9, 10)
        self.client.setRebuildCallback(lambda: self.rebuildLater.emit())
        self.client.setRefreshCallback(lambda: self.refreshLater.emit())

        self.buildUi()

    @pyqtSlot()
    def buildUi(self):
        self.cells = []
        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(2)
        for i in range(self.client.height()):
            self.cells.append([])
            for j in range(self.client.width()):
                self.cells[i].append(CellWidget(self, j, i))
                self.gridLayout.addWidget(self.cells[i][j], i, j)

        # 레이아웃을 다른 위젯으로 옮겨서 삭제함
        if self.layout() is not None:
            tmp = QWidget()
            tmp.setLayout(self.layout())

        self.setLayout(self.gridLayout)
        self.update()

        self.refreshed.emit()

    @pyqtSlot()
    def updateUi(self):
        for row in self.cells:
            for cell in row:
                cell.updateDisplay()

        self.refreshed.emit()

    def getCell(self, x, y):
        return self.cells[y][x]

    def height(self):
        return self.client.height()

    def width(self):
        return self.client.width()
