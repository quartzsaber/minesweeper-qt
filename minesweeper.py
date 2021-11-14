import sys

from PyQt5.QtWidgets import QApplication

from gamewindow import GameWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = GameWindow()
    game.show()
    sys.exit(app.exec_())
