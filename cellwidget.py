from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolButton

from constants import *
if TYPE_CHECKING:
    from gamewidget import GameWidget

STYLESHEET = '''
CellWidget {
    background-color: #eeeeee;
    font-family: Arial;
    font-weight: bold;
    font-size: 24px;
    line-height: 24px;
}

CellWidget[opened="yes"] {
    background-color: #dddddd;
    border: none;
}

CellWidget[colorize="1"] { color: #0000ff; }
CellWidget[colorize="2"] { color: #008000; }
CellWidget[colorize="3"] { color: #ff0000; }
CellWidget[colorize="4"] { color: #000080; }
CellWidget[colorize="5"] { color: #800000; }
CellWidget[colorize="6"] { color: #008080; }
CellWidget[colorize="7"] { color: #000000; }
CellWidget[colorize="8"] { color: #808080; }
CellWidget[missed="yes"] { background-color: #dd0000; }
'''

# 숫자를 Unicode Full Width Character로 매핑해놓은 맵
FULLWIDTH_MAP = {0: '０', 1: '１', 2: '２', 3: '３', 4: '４', 5: '５', 6: '６', 7: '７', 8: '８'}

# 이미지 상수를 실제 이미지로 매핑해놓은 맵
IMAGE_RESOURCE_MAP = {
    ImageType.NONE: None,
    ImageType.FLAG: 'image-flag.png',
    ImageType.QUESTION: 'image-question.png',
    ImageType.BLOWN_UP_MINE: 'image-mine.png',
    ImageType.MISSED_MINE: 'image-mine.png',
    ImageType.WRONG_FLAG: 'image-flag.png',
}

# 배경이 빨간색인 이미지들
IMAGES_MISSED = {ImageType.MISSED_MINE, ImageType.WRONG_FLAG}


# 현재 버튼이 마우스에 의해 눌리고 있는지 여부
class MouseState(IntEnum):
    NONE = 0
    LEFT = 1
    MIDDLE = 2
    RIGHT = 3


class CellWidget(QToolButton):
    def __init__(self, gameWidget, x, y):
        super(QToolButton, self).__init__()

        self.x = x
        self.y = y
        self.gameWidget = gameWidget  # type: GameWidget
        self.mouseState = MouseState.NONE

        self.setStyleSheet(STYLESHEET)
        self.updateDisplay()

    def updateDown(self, newDown):
        if self.mouseState == MouseState.LEFT:
            self.trySetDown(newDown)
        elif self.mouseState == MouseState.MIDDLE:
            for i in range(-1, 2):
                if 0 <= self.x + i < self.gameWidget.height():
                    for j in range(-1, 2):
                        if 0 <= self.y + j < self.gameWidget.width():
                            self.gameWidget.getCell(self.x + i, self.y + j).trySetDown(newDown)

    def trySetDown(self, newDown):
        text = self.gameWidget.client.getCellText(self.x, self.y)
        image = self.gameWidget.client.getCellImage(self.x, self.y)
        if text is None and image != ImageType.FLAG:
            self.setDown(newDown)
        else:
            self.setDown(False)

    def updateDisplay(self):
        image = self.gameWidget.client.getCellImage(self.x, self.y)
        text = self.gameWidget.client.getCellText(self.x, self.y)
        opened = text is not None

        newProps = {}

        if image == ImageType.NONE:
            colorizeKey = text
            if text is None:
                text = ''
                opened = False
            elif text == 0:
                text = ''
            else:
                text = FULLWIDTH_MAP[text]

            self.setIcon(QIcon())
            self.setText(text)
            newProps["colorize"] = str(colorizeKey)
            newProps["missed"] = "no"
        else:
            imgPath = IMAGE_RESOURCE_MAP[image]
            self.setIcon(QIcon(f"{RESOURCE_PATH}/{imgPath}"))
            self.setText('')
            newProps["colorize"] = ""
            newProps["missed"] = "yes" if image in IMAGES_MISSED else "no"

        newProps["opened"] = "yes" if opened else "no"

        # Polishing은 시간이 오래 걸리므로 꼭 필요한 경우에만 진행
        if any((self.property(k) != v for k, v in newProps.items())):
            for k, v in newProps.items():
                self.setProperty(k, v)

            self.style().unpolish(self)
            self.ensurePolished()

    def sizeHint(self):
        return QSize(24, 24)

    def mousePressEvent(self, event):
        event.accept()
        if self.mouseState != MouseState.NONE or self.gameWidget.client.checkFinished():
            return

        if event.button() == Qt.LeftButton:
            self.mouseState = MouseState.LEFT
            self.updateDown(True)
        elif event.button() == Qt.MiddleButton:
            self.mouseState = MouseState.MIDDLE
            self.updateDown(True)
        elif event.button() == Qt.RightButton:
            self.mouseState = MouseState.RIGHT

    # 이 위젯은 마우스 트래킹이 꺼져있기 때문에 마우스 버튼이 눌린 상태에서만 이 함수가 불림
    def mouseMoveEvent(self, event):
        event.accept()
        if self.mouseState == MouseState.LEFT or self.mouseState == MouseState.MIDDLE:
            self.updateDown(self.rect().contains(event.pos()))

    def mouseReleaseEvent(self, event):
        event.accept()
        if self.rect().contains(event.pos()):
            if self.mouseState == MouseState.LEFT:
                self.gameWidget.client.openCell(self.x, self.y)
            elif self.mouseState == MouseState.MIDDLE:
                self.gameWidget.client.openCellAdjacent(self.x, self.y)
            elif self.mouseState == MouseState.RIGHT:
                self.gameWidget.client.cycleCellImage(self.x, self.y)
        self.updateDown(False)
        self.mouseState = MouseState.NONE
