from PyQt5.QtWidgets import QWidget, QGridLayout

from gameboard import GameBoard
from cellwidget import CellWidget


class GameWidget(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        
        self.board = GameBoard()
        self.board.new_game(9, 9, 10)
        
        self.cells = []
        self.cell_grid = QGridLayout()
        self.cell_grid.setSpacing(2)
        for i in range(self.board.height()):
            self.cells.append([])
            for j in range(self.board.width()):
                self.cells[i].append(CellWidget(self, j, i))
                self.cell_grid.addWidget(self.cells[i][j], i, j)
        
        self.setLayout(self.cell_grid)
    
    def updateAll(self):
        for row in self.cells:
            for cell in row:
                cell.updateDisplay()
    
    def getCell(self, x, y):
        return self.cells[y][x]
    
    def height(self):
        return len(self.cells)
    
    def width(self):
        return len(self.cells[0])
