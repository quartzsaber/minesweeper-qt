from PyQt5.QtWidgets import QMainWindow, QLabel

from gamewidget import GameWidget


class GameWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        
        self.gamewidget = GameWidget()
        
        self.setWindowTitle('지뢰찾기')
        self.setCentralWidget(self.gamewidget)
