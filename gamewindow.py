import sys

from PyQt5.QtCore import pyqtSlot, QTimer, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QLayout, QDialog, QGridLayout, QLabel, QMessageBox, QLineEdit, \
    QDialogButtonBox, QFrame, QToolButton
from PyQt5.QtWidgets import QLCDNumber
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

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

        self.mineIcon = QIcon('resource/image-mine.png')
        self.setWindowIcon(self.mineIcon)

        if sys.platform == 'win32':
            self.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)

        self.gameWidget = GameWidget(9, 9, 10)
        self.gameWidget.refreshBoard.connect(self.refreshScore)
        self.setWindowTitle('지뢰찾기')
        self.setFixedSize(0, 0)

        self.setupMenu()
        self.setupUi()

        self.timeUpdatingTimer = QTimer()
        self.timeUpdatingTimer.timeout.connect(self.refreshTime)
        self.timeUpdatingTimer.start(1000)

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
        action.setToolTip('22x22에 지뢰 97개')
        action.triggered.connect(lambda: self.newGame(22, 22, 97))

        action = menu.addAction('커스텀')
        action.triggered.connect(self.customGame)

        menu = menuBar.addMenu('협동 모드')
        action = menu.addAction('참가하기')
        action.setToolTip('다른 사람이 연 방에 들어갑니다')
        action.triggered.connect(self.joinServer)

        action = menu.addAction('방 만들기')
        action.setToolTip('다른 사람이 들어올 수 있게 방을 엽니다')
        action.triggered.connect(self.openServer)

    def setupUi(self):
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

    @pyqtSlot()
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

    @pyqtSlot()
    def resetGame(self):
        self.newGame(self.gameWidget.width(), self.gameWidget.height(), self.gameWidget.board.countMine())

    @pyqtSlot(int, int, int)
    def newGame(self, width: int, height: int, mines: int):
        self.gameWidget = GameWidget(width, height, mines)
        self.gameWidget.refreshBoard.connect(self.refreshScore)
        self.setupUi()

    @pyqtSlot()
    def joinServer(self):
        print('STUB: joinServer')

    @pyqtSlot()
    def openServer(self):
        print('STUB: openServer')

    @pyqtSlot()
    def refreshScore(self):
        self.scoreDisplay.display(self.gameWidget.board.countRemainingMine())
        self.refreshTime()

    @pyqtSlot()
    def refreshTime(self):
        s = int(self.gameWidget.board.getPlaytime())
        m = s // 60
        s %= 60
        if m > 99:
            m = 99
            s = 59
        self.timeDisplay.display(f'{m:02d}:{s:02d}')
