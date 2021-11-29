from typing import Optional

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QCoreApplication, Qt
from PyQt5.QtWidgets import QFrame, QGridLayout, QWidget, QMessageBox, QDialogButtonBox

from cellwidget import CellWidget
from networkclient import NetworkClient
from serverrole import IServerRole
from clientrole import IClientRole
from integratedserver import IntegratedServer


class GameWidget(QFrame):
    refreshed = pyqtSignal()
    disconnected = pyqtSignal(str)
    rebuildLater = pyqtSignal()
    refreshLater = pyqtSignal()

    def __init__(self):
        super(QFrame, self).__init__()
        self.disconnected.connect(self.onDisconnected)
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

    def ensureIntegratedServer(self):
        if not isinstance(self.server, IntegratedServer):
            box = QMessageBox(self.window())
            box.setWindowTitle('네트워크 중단')
            box.setText('정말로 다른 컴퓨터와의 연결을 끊겠습니까?')
            box.setIcon(QMessageBox.Question)
            box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            btn = box.exec()
            if btn != QMessageBox.Ok:
                return False

            w = max(9, self.client.width())
            h = max(9, self.client.height())
            m = max(10, self.client.countMine())
            integratedServer = IntegratedServer()
            integratedServer.newGame(w, h, m)
            self.server = integratedServer
            self.client = integratedServer
            self.client.setRebuildCallback(lambda: self.rebuildLater.emit())
            self.client.setRefreshCallback(lambda: self.refreshLater.emit())
            self.rebuildLater.emit()

        return True

    def resetGame(self):
        if self.ensureIntegratedServer():
            self.server.newGameSameConfig()

    def newGame(self, w, h, m):
        if self.ensureIntegratedServer():
            self.server.newGame(w, h, m)

    def joinServer(self, addr, pin):
        networkClient = NetworkClient(addr, pin)
        networkClient.setDisconnectedCallback(lambda reason: self.disconnected.emit(reason))
        self.server = None
        self.client = networkClient
        self.client.setRebuildCallback(lambda: self.rebuildLater.emit())
        self.client.setRefreshCallback(lambda: self.refreshLater.emit())

    def openServer(self):
        if self.ensureIntegratedServer():
            if not self.server.startListening():
                box = QMessageBox(self.window())
                box.setWindowTitle('네트워크 오류')
                box.setIcon(QMessageBox.Critical)
                box.setText('알 수 없는 네트워크 오류로 인해 서버를 열지 못했습니다.')
                box.setStandardButtons(QMessageBox.Cancel)
                box.buttonClicked.connect(box.deleteLater)
                box.show()
                return

            info = self.server.getHostingInfo()
            box = QMessageBox(self.window())
            box.setWindowTitle('연결 정보')
            box.setIcon(QMessageBox.Information)
            box.setText(f"""핀 번호: {info['pin']}

Tip. 쉽게 연결하기 위해서 LogMeIn Hamachi 등의
서비스를 이용하는 것을 권장합니다.""")
            box.setStandardButtons(QMessageBox.Ok)
            box.buttonClicked.connect(box.deleteLater)
            box.show()

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

    @pyqtSlot(str)
    def onDisconnected(self, reason):
        box = QMessageBox(self.window())
        box.setWindowTitle('네트워크 오류')
        box.setIcon(QMessageBox.Critical)
        box.setText(reason)
        box.setStandardButtons(QMessageBox.Close)
        box.buttonClicked.connect(box.deleteLater)
        box.show()

    def getCell(self, x, y):
        return self.cells[y][x]

    def height(self):
        return self.client.height()

    def width(self):
        return self.client.width()
