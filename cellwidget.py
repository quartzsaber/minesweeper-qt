from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolButton

from gameboard import IMAGE_NONE, IMAGE_FLAG, IMAGE_QUESTION, IMAGE_BLOWN_UP_MINE, IMAGE_MISSED_MINE, IMAGE_WRONG_FLAG


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
CellWidget[missed="yes"] { background-color: #ff0000; }
'''


# 숫자를 Unicode Full Width Character로 매핑해놓은 맵
FULLWIDTH_MAP = {0: '０', 1: '１', 2: '２', 3: '３', 4: '４', 5: '５', 6: '６', 7: '７', 8: '８' }

# 이미지 상수를 실제 이미지로 매핑해놓은 맵
IMAGE_RESOURCE_MAP = {
    IMAGE_NONE: None,
    IMAGE_FLAG: 'image-flag.png',
    IMAGE_QUESTION: 'image-question.png',
    IMAGE_BLOWN_UP_MINE: 'image-mine.png',
    IMAGE_MISSED_MINE: 'image-mine.png',
    IMAGE_WRONG_FLAG: 'image-flag.png',
}

# 배경이 빨간색인 이미지들
IMAGES_MISSED = { IMAGE_MISSED_MINE, IMAGE_WRONG_FLAG }

# 현재 버튼이 마우스에 의해 눌리고 있는지 여부
PRESS_STATE_NONE = 0
PRESS_STATE_LEFT = 1
PRESS_STATE_MIDDLE = 2
PRESS_STATE_RIGHT = 3


class CellWidget(QToolButton):
    def __init__(self, gamewidget, x, y):
        super(QToolButton, self).__init__()
        
        self.x = x
        self.y = y
        self.gamewidget = gamewidget
        self.pressState = PRESS_STATE_NONE
        
        self.setStyleSheet(STYLESHEET)
        self.updateDisplay()
    
    def updateDown(self, newDown):
        if self.pressState == PRESS_STATE_LEFT:
            self.trySetDown(newDown)
        elif self.pressState == PRESS_STATE_MIDDLE:
            for i in range(-1, 2):
                if 0 <= self.x + i < self.gamewidget.height():
                    for j in range(-1, 2):
                        if 0 <= self.y + j < self.gamewidget.width():
                            self.gamewidget.getCell(self.x + i, self.y + j).trySetDown(newDown)
    
    def trySetDown(self, newDown):
        text = self.gamewidget.board.get_cell_text(self.x, self.y)
        image = self.gamewidget.board.get_cell_image(self.x, self.y)
        if text is None and image != IMAGE_FLAG:
            self.setDown(newDown)
    
    def updateDisplay(self):
        dirty = False
        
        image = self.gamewidget.board.get_cell_image(self.x, self.y)
        text = self.gamewidget.board.get_cell_text(self.x, self.y)
        opened = text is not None
        
        if image == IMAGE_NONE:
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
            self.setProperty("colorize", str(colorizeKey))
            self.setProperty("miss", "yes" if image in IMAGES_MISSED else "no")
        else:
            imgPath = IMAGE_RESOURCE_MAP[image]
            self.setIcon(QIcon(f"resource/{imgPath}"))
            self.setText('')
            self.setProperty("colorize", "")
            self.setProperty("miss", "yes" if image in IMAGES_MISSED else "no")
        
        self.setProperty("opened", "yes" if opened else "no")
        self.style().unpolish(self)
        self.ensurePolished()
    
    def sizeHint(self):
        return QSize(24, 24)
    
    def mousePressEvent(self, event):
        event.accept()
        if self.pressState != PRESS_STATE_NONE:
            return
        
        if event.button() == Qt.LeftButton:
            self.pressState = PRESS_STATE_LEFT
            self.updateDown(True)
        elif event.button() == Qt.MiddleButton:
            self.pressState = PRESS_STATE_MIDDLE
            self.updateDown(True)
        elif event.button() == Qt.RightButton:
            self.pressState = PRESS_STATE_RIGHT
    
    # 이 위젯은 마우스 트래킹이 꺼져있기 때문에 마우스 버튼이 눌린 상태에서만 이 함수가 불림
    def mouseMoveEvent(self, event):
        event.accept()
        if self.pressState == PRESS_STATE_LEFT or self.pressState == PRESS_STATE_MIDDLE:
            self.updateDown(self.rect().contains(event.pos()))
    
    def mouseReleaseEvent(self, event):
        event.accept()
        if self.rect().contains(event.pos()):
            if self.pressState == PRESS_STATE_LEFT:
                self.gamewidget.board.open_cell(self.x, self.y)
            elif self.pressState == PRESS_STATE_MIDDLE:
                self.gamewidget.board.open_cell_adjacent(self.x, self.y)
            elif self.pressState == PRESS_STATE_RIGHT:
                self.gamewidget.board.cycle_cell_image(self.x, self.y)
        self.updateDown(False)
        self.gamewidget.updateAll()
        self.pressState = PRESS_STATE_NONE
