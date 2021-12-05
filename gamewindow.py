import sys
import os

from PyQt5.QtCore import pyqtSlot, QTimer, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QLayout, QDialog, QGridLayout
from PyQt5.QtWidgets import QLabel, QMessageBox, QLineEdit, QDialogButtonBox
from PyQt5.QtWidgets import QLCDNumber, QFrame, QToolButton
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

from constants import RESOURCE_PATH
from gamewidget import GameWidget


STYLESHEET = '''
QLCDNumber {
    background-color: #000000;
    color: #ff0000;
}
'''


def setupLcdStyle(lcd: QLCDNumber):
    lcd.setFixedSize(80, 30)
    lcd.setStyleSheet(STYLESHEET)
    lcd.setDigitCount(5)
    lcd.setSegmentStyle(QLCDNumber.Flat)
    lcd.display('')


class GameWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()

        self.mineIcon = QIcon(f'{RESOURCE_PATH}/image-mine.png')
        self.setWindowIcon(self.mineIcon)

        if sys.platform == 'win32':
            self.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        self.gameWidget = GameWidget()
        self.gameWidget.refreshed.connect(self.refreshScore)
        self.setWindowTitle('지뢰찾기')
        self.setFixedSize(0, 0)

        self.setupMenu()
        self.buildUi()

        self.timeUpdatingTimer = QTimer()
        self.timeUpdatingTimer.timeout.connect(self.refreshTime)
        self.timeUpdatingTimer.start(250)

    def paintEvent(self, ev):
        super().paintEvent(ev)
        if self.height() != self.minimumHeight() or self.width() != self.minimumWidth():
            self.resize(0, 0)

    def setupMenu(self):
        menuBar = self.menuBar()
        menu = menuBar.addMenu('새 게임')
        action = menu.addAction('초급')
        action.setToolTip('9x9에 지뢰 10개')
        action.triggered.connect(lambda: self.newGame(9, 9, 10))

        action = menu.addAction('중급')
        action.setToolTip('16x16에 지뢰 40개')
        action.triggered.connect(lambda: self.newGame(16, 16, 40))

        action = menu.addAction('고급')
        action.setToolTip('25x25에 지뢰 60개')
        action.triggered.connect(lambda: self.newGame(25, 25, 60))

        action = menu.addAction('커스텀')
        action.triggered.connect(self.customGame)

        menu = menuBar.addMenu('협동 모드')
        action = menu.addAction('참가하기')
        action.setToolTip('다른 사람이 연 방에 들어갑니다')
        action.triggered.connect(self.joinServer)

        action = menu.addAction('방 만들기')
        action.setToolTip('다른 사람이 들어올 수 있게 방을 엽니다')
        action.triggered.connect(self.openServer)

    def buildUi(self):
        self.mainWidget = QWidget()

        self.scoreDisplay = QLCDNumber()
        self.scoreDisplay.setToolTip('남은 지뢰 수')
        setupLcdStyle(self.scoreDisplay)

        self.timeDisplay = QLCDNumber()
        self.timeDisplay.setToolTip('게임 시간')
        setupLcdStyle(self.timeDisplay)

        self.refreshScore()

        resetButton = QToolButton()
        resetButton.setIcon(self.mineIcon)
        resetButton.setToolTip('리셋')
        resetButton.clicked.connect(self.resetGame)

        topBox = QFrame()
        topBox.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        topLayout = QHBoxLayout(topBox)
        topLayout.addWidget(self.scoreDisplay)
        topLayout.addStretch()
        topLayout.addWidget(resetButton)
        topLayout.addStretch()
        topLayout.addWidget(self.timeDisplay)

        rootLayout = QVBoxLayout()
        rootLayout.setSizeConstraint(QLayout.SetFixedSize)
        rootLayout.addWidget(topBox)
        rootLayout.addWidget(self.gameWidget)
        self.mainWidget.setLayout(rootLayout)

        self.setCentralWidget(self.mainWidget)

    def customGame(self):
        dialog = QDialog(self)
        dialog.setSizeGripEnabled(False)
        dialog.setWindowTitle('커스텀 게임')

        if sys.platform == 'win32':
            dialog.setWindowFlags(dialog.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        width = QLineEdit('9')
        height = QLineEdit('9')
        mines = QLineEdit('10')
        btn = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout = QGridLayout(dialog)
        layout.addWidget(QLabel('가로'), 1, 1)
        layout.addWidget(QLabel('세로'), 2, 1)
        layout.addWidget(QLabel('지뢰 개수'), 3, 1)
        layout.addWidget(width, 1, 2)
        layout.addWidget(height, 2, 2)
        layout.addWidget(mines, 3, 2)
        layout.addWidget(btn, 4, 1, 1, 2)

        def onAccepted():
            try:
                w = max(9, int(width.text()))
                h = max(9, int(height.text()))
                m = max(10, int(mines.text()))
                self.newGame(w, h, m)
            except ValueError:
                pass
            finally:
                dialog.destroy()

        btn.accepted.connect(onAccepted)
        btn.rejected.connect(dialog.destroy)

        dialog.show()

    def resetGame(self):
        self.gameWidget.resetGame()

    def newGame(self, width: int, height: int, mines: int):
        self.gameWidget.newGame(width, height, mines)

    def joinServer(self):
        dialog = QDialog(self)
        dialog.setSizeGripEnabled(False)
        dialog.setWindowTitle('게임 참가')

        if sys.platform == 'win32':
            dialog.setWindowFlags(dialog.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        addrEdit = QLineEdit()
        pinEdit = QLineEdit()

        addrEdit.setPlaceholderText('127.0.0.1')
        pinEdit.setPlaceholderText('0000')

        btn = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout = QGridLayout(dialog)
        layout.addWidget(QLabel('IP 주소'), 1, 1)
        layout.addWidget(QLabel('핀 번호'), 2, 1)
        layout.addWidget(addrEdit, 1, 2)
        layout.addWidget(pinEdit, 2, 2)
        layout.addWidget(btn, 3, 1, 1, 2)

        def onAccepted():
            try:
                addr = str(addrEdit.text())
                if len(addr) == 0:
                    addr = '127.0.0.1'

                pin = int(pinEdit.text())
                if pin <= 0 or pin > 9999:
                    raise ValueError('Pin out of range')

                self.gameWidget.joinServer(addr, pin)
            except ValueError:
                box = QMessageBox(self.window())
                box.setWindowTitle('오류')
                box.setIcon(QMessageBox.Critical)
                box.setText('핀 번호는 0000 에서 9999 사이의 숫자입니다.')
                box.setStandardButtons(QMessageBox.Close)
                box.buttonClicked.connect(box.deleteLater)
                box.show()
            finally:
                dialog.destroy()

        btn.accepted.connect(onAccepted)
        btn.rejected.connect(dialog.destroy)

        dialog.show()

    def openServer(self):
        self.gameWidget.openServer()

    @pyqtSlot()
    def refreshScore(self):
        self.scoreDisplay.display(self.gameWidget.client.countRemainingMine())
        self.refreshTime()

    @pyqtSlot()
    def refreshTime(self):
        s = int(self.gameWidget.client.getPlaytime())
        m = s // 60
        s %= 60
        if m > 99:
            m = 99
            s = 59
        self.timeDisplay.display(f'{m:02d}:{s:02d}')
