import unittest

from gameboard import *


class GameBoardTestCase(unittest.TestCase):
    def setUp(self):
        self.game = GameBoard()
        self.game.newGame(7, 5, 0)
        self.game.mines[0][0] = True
        self.game.mines[1][1] = True
        self.game.mines[2][2] = True

    def test_newGame(self):
        self.game.newGame(7, 5, 3)
        cnt = 0
        for i in range(len(self.game.mines)):
            for j in range(len(self.game.mines[i])):
                if self.game.mines[i][j]:
                    cnt += 1
        self.assertEqual(cnt, 3)

    def test_serialization(self):
        self.assertEqual(type(self.game.serializeGame()), type(b''))
        self.game.deserializeGame(self.game.serializeGame())

    def test_cycleCellImage(self):
        self.assertEqual(self.game.getCellImage(0, 0), IMAGE_NONE)
        self.game.cycleCellImage(0, 0)
        self.assertEqual(self.game.getCellImage(0, 0), IMAGE_FLAG)
        self.game.cycleCellImage(0, 0)
        self.assertEqual(self.game.getCellImage(0, 0), IMAGE_QUESTION)
        self.game.cycleCellImage(0, 0)
        self.assertEqual(self.game.getCellImage(0, 0), IMAGE_NONE)

    def test_openCell(self):
        self.assertEqual(self.game.openCell(0, 1), False)
        self.assertEqual(self.game.getCellImage(0, 0), IMAGE_NONE)
        self.assertEqual(self.game.openCell(0, 0), True)
        self.assertEqual(self.game.getCellImage(0, 0), IMAGE_BLOWN_UP_MINE)
        self.assertEqual(self.game.openCell(0, 0), False)
        self.game.cycleCellImage(1, 1)
        self.assertEqual(self.game.openCell(1, 1), False)
        self.assertEqual(self.game.getCellImage(1, 1), IMAGE_FLAG)
        self.game.cycleCellImage(1, 1)
        self.assertEqual(self.game.getCellImage(1, 1), IMAGE_QUESTION)
        self.assertEqual(self.game.openCell(1, 1), True)
        self.assertEqual(self.game.getCellImage(1, 1), IMAGE_BLOWN_UP_MINE)

        self.game.images[2][2] = IMAGE_BLOWN_UP_MINE
        self.assertEqual(self.game.openCell(2, 2), False)

        self.assertEqual(self.game.openCell(6, 4), False)

    def test_openCellAdjacent(self):
        self.game.cycleCellImage(0, 0)
        self.game.cycleCellImage(1, 1)
        self.game.cycleCellImage(2, 2)
        self.assertEqual(self.game.openCellAdjacent(1, 1), False)
        self.assertEqual(self.game.openCellAdjacent(0, 0), False)
        self.assertEqual(self.game.getCellImage(0, 0), IMAGE_FLAG)
        self.assertEqual(self.game.getCellImage(1, 1), IMAGE_FLAG)
        self.assertEqual(self.game.getCellImage(2, 2), IMAGE_FLAG)

        self.game.cycleCellImage(2, 2)
        self.assertEqual(self.game.openCellAdjacent(0, 0), False)
        self.assertEqual(self.game.getCellImage(0, 0), IMAGE_FLAG)
        self.assertEqual(self.game.getCellImage(1, 1), IMAGE_FLAG)
        self.assertEqual(self.game.getCellImage(2, 2), IMAGE_QUESTION)

        self.game.cycleCellImage(0, 0)
        self.assertEqual(self.game.openCellAdjacent(1, 1), True)
        self.assertEqual(self.game.getCellImage(0, 0), IMAGE_BLOWN_UP_MINE)
        self.assertEqual(self.game.getCellImage(1, 1), IMAGE_FLAG)
        self.assertEqual(self.game.getCellImage(2, 2), IMAGE_BLOWN_UP_MINE)

        self.game.openCellAdjacent(4, 1)
        for i in [3, 4, 5]:
            for j in [0, 1, 2]:
                self.assertTrue(self.game.getCellText(i, j) >= 0)
        self.assertTrue(self.game.getCellText(6, 0) == 0)

        self.assertEqual(self.game.openCellAdjacent(6, 4), False)

    def test_finishGame(self):
        self.game.mines[3][3] = True

        self.game.cycleCellImage(0, 0)
        self.game.cycleCellImage(0, 1)
        self.game.cycleCellImage(2, 2)
        self.game.cycleCellImage(2, 2)

        self.assertEqual(self.game.getCellImage(0, 0), IMAGE_FLAG)
        self.assertEqual(self.game.getCellImage(0, 1), IMAGE_FLAG)
        self.assertEqual(self.game.getCellImage(1, 1), IMAGE_NONE)
        self.assertEqual(self.game.getCellImage(2, 2), IMAGE_QUESTION)

        self.assertEqual(self.game.openCell(3, 3), True)
        self.game.finishGame()

        self.assertEqual(self.game.getCellImage(0, 0), IMAGE_FLAG)
        self.assertEqual(self.game.getCellImage(0, 1), IMAGE_WRONG_FLAG)
        self.assertEqual(self.game.getCellImage(1, 1), IMAGE_MISSED_MINE)
        self.assertEqual(self.game.getCellImage(2, 2), IMAGE_MISSED_MINE)
        self.assertEqual(self.game.getCellImage(3, 3), IMAGE_BLOWN_UP_MINE)

    def test_countRemainingMine(self):
        self.assertEqual(self.game.countRemainingMine(), 3)
        self.game.cycleCellImage(0, 0)
        self.assertEqual(self.game.countRemainingMine(), 2)
        self.game.cycleCellImage(0, 0)
        self.assertEqual(self.game.countRemainingMine(), 3)
        self.game.cycleCellImage(0, 0)
        self.game.cycleCellImage(0, 0)
        self.game.cycleCellImage(0, 1)
        self.assertEqual(self.game.countRemainingMine(), 1)
        self.game.cycleCellImage(0, 2)
        self.assertEqual(self.game.countRemainingMine(), 0)
        self.game.cycleCellImage(0, 3)
        self.assertEqual(self.game.countRemainingMine(), -1)

    def test_countMine(self):
        self.assertEqual(self.game.countMine(), 3)
        self.game.cycleCellImage(0, 0)
        self.game.cycleCellImage(1, 1)
        self.assertEqual(self.game.countMine(), 3)
        self.game.cycleCellImage(0, 0)
        self.assertEqual(self.game.countMine(), 3)
        self.game.mines[4][6] = True
        self.assertEqual(self.game.countMine(), 4)

    def test_check_finished(self):
        self.game.cycleCellImage(2, 2)

        self.assertEqual(self.game.checkFinished(), False)
        self.assertEqual(self.game.openCell(1, 0), False)
        self.assertEqual(self.game.openCellAdjacent(3, 1), False)
        self.assertEqual(self.game.openCellAdjacent(5, 1), False)
        for x in range(7):
            for y in range(3, 5):
                self.assertEqual(self.game.openCell(x, y), False)
        self.assertEqual(self.game.openCellAdjacent(0, 2), True)
        self.assertEqual(self.game.checkFinished(), True)

    def test_get_cell_text(self):
        self.assertEqual(self.game.getCellText(0, 0), None)
        self.assertEqual(self.game.getCellText(0, 1), None)

        self.game.openCell(0, 1)
        self.game.openCellAdjacent(4, 1)
        self.assertEqual(self.game.getCellText(0, 1), 2)
        self.assertEqual(self.game.getCellText(0, 2), 1)
        self.assertEqual(self.game.getCellText(0, 3), 0)

        self.assertEqual(self.game.getCellText(1, 0), None)
        self.assertEqual(self.game.getCellText(2, 0), 1)
        self.assertEqual(self.game.getCellText(3, 0), 0)

        self.game.openCell(1, 1)
        self.assertEqual(self.game.getCellText(1, 1), 3)

    def test_count_adjacent_mine(self):
        self.game.mines[4][6] = True

        self.assertEqual(self.game.countAdjacentMines(1, 1), 3)
        self.assertEqual(self.game.countAdjacentMines(0, 0), 2)
        self.assertEqual(self.game.countAdjacentMines(2, 2), 2)
        self.assertEqual(self.game.countAdjacentMines(3, 0), 0)
        self.assertEqual(self.game.countAdjacentMines(6, 4), 1)
        self.assertEqual(self.game.countAdjacentMines(5, 4), 1)
        self.assertEqual(self.game.countAdjacentMines(6, 3), 1)

    def test_iter_empty_adjacent(self):
        self.game.mines[3][2] = True
        self.game.mines[4][2] = True
        self.game.mines[2][4] = True
        self.game.mines[2][5] = True
        self.game.mines[2][6] = True

        self.assertEqual(sum([1 for x in self.game.iterEmptyAdjacent(0, 2)]), 1)
        self.assertEqual(sum([1 for x in self.game.iterEmptyAdjacent(0, 3)]), 6)
        self.assertEqual(sum([1 for x in self.game.iterEmptyAdjacent(0, 0)]), 1)
        self.assertEqual(sum([1 for x in self.game.iterEmptyAdjacent(2, 0)]), 1)
        self.assertEqual(sum([1 for x in self.game.iterEmptyAdjacent(3, 0)]), 10)
        self.assertEqual(sum([1 for x in self.game.iterEmptyAdjacent(6, 4)]), 8)


if __name__ == '__main__':
    unittest.main()
