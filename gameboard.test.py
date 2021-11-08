import unittest

from gameboard import *


class GameBoardTestCase(unittest.TestCase):
    def setUp(self):
        self.game = GameBoard()
        self.game.new_game(7, 5, 0)
        self.game.mines[0][0] = True
        self.game.mines[1][1] = True
        self.game.mines[2][2] = True
    
    def test_new_game(self):
        self.game.new_game(7, 5, 3)
        cnt = 0
        for i in range(len(self.game.mines)):
            for j in range(len(self.game.mines[i])):
                if self.game.mines[i][j]:
                    cnt += 1
        self.assertEqual(cnt, 3)
    
    def test_serialization(self):
        self.assertEqual(type(self.game.serialize_game()), type(b''))
        self.game.deserialize_game(self.game.serialize_game())
    
    def test_cycle_cell_image(self):
        self.assertEqual(self.game.get_cell_image(0, 0), IMAGE_NONE)
        self.game.cycle_cell_image(0, 0)
        self.assertEqual(self.game.get_cell_image(0, 0), IMAGE_FLAG)
        self.game.cycle_cell_image(0, 0)
        self.assertEqual(self.game.get_cell_image(0, 0), IMAGE_QUESTION)
        self.game.cycle_cell_image(0, 0)
        self.assertEqual(self.game.get_cell_image(0, 0), IMAGE_NONE)
    
    def test_open_cell(self):
        self.assertEqual(self.game.open_cell(0, 1), False)
        self.assertEqual(self.game.get_cell_image(0, 0), IMAGE_NONE)
        self.assertEqual(self.game.open_cell(0, 0), True)
        self.assertEqual(self.game.get_cell_image(0, 0), IMAGE_BLOWN_UP_MINE)
        self.assertEqual(self.game.open_cell(0, 0), False)
        self.game.cycle_cell_image(1, 1)
        self.assertEqual(self.game.open_cell(1, 1), False)
        self.assertEqual(self.game.get_cell_image(1, 1), IMAGE_FLAG)
        self.game.cycle_cell_image(1, 1)
        self.assertEqual(self.game.get_cell_image(1, 1), IMAGE_QUESTION)
        self.assertEqual(self.game.open_cell(1, 1), True)
        self.assertEqual(self.game.get_cell_image(1, 1), IMAGE_BLOWN_UP_MINE)
        
        self.game.images[2][2] = IMAGE_BLOWN_UP_MINE
        self.assertEqual(self.game.open_cell(2, 2), False)
    
    def test_open_cell_adjacent(self):
        self.game.cycle_cell_image(0, 0)
        self.game.cycle_cell_image(1, 1)
        self.game.cycle_cell_image(2, 2)
        self.assertEqual(self.game.open_cell_adjacent(1, 1), False)
        self.assertEqual(self.game.open_cell_adjacent(0, 0), False)
        self.assertEqual(self.game.get_cell_image(0, 0), IMAGE_FLAG)
        self.assertEqual(self.game.get_cell_image(1, 1), IMAGE_FLAG)
        self.assertEqual(self.game.get_cell_image(2, 2), IMAGE_FLAG)
        
        self.game.cycle_cell_image(2, 2)
        self.assertEqual(self.game.open_cell_adjacent(0, 0), False)
        self.assertEqual(self.game.get_cell_image(0, 0), IMAGE_FLAG)
        self.assertEqual(self.game.get_cell_image(1, 1), IMAGE_FLAG)
        self.assertEqual(self.game.get_cell_image(2, 2), IMAGE_QUESTION)
        
        self.game.cycle_cell_image(0, 0)
        self.assertEqual(self.game.open_cell_adjacent(1, 1), True)
        self.assertEqual(self.game.get_cell_image(0, 0), IMAGE_BLOWN_UP_MINE)
        self.assertEqual(self.game.get_cell_image(1, 1), IMAGE_BLOWN_UP_MINE)
        self.assertEqual(self.game.get_cell_image(2, 2), IMAGE_QUESTION)
        
        self.game.open_cell_adjacent(4, 1)
        for i in [3, 4, 5]:
            for j in [0, 1, 2]:
                self.assertTrue(self.game.get_cell_text(i, j) >= 0)
        self.assertTrue(self.game.get_cell_text(6, 0) == 0)
        
        self.assertEqual(self.game.open_cell_adjacent(6, 4), False)
    
    def test_count_remaining_mine(self):
        self.assertEqual(self.game.count_remaining_mine(), 3)
        self.game.cycle_cell_image(0, 0)
        self.assertEqual(self.game.count_remaining_mine(), 2)
        self.game.cycle_cell_image(0, 0)
        self.assertEqual(self.game.count_remaining_mine(), 3)
        self.game.cycle_cell_image(0, 0)
        self.game.cycle_cell_image(0, 0)
        self.game.cycle_cell_image(0, 1)
        self.assertEqual(self.game.count_remaining_mine(), 1)
        self.game.cycle_cell_image(0, 2)
        self.assertEqual(self.game.count_remaining_mine(), 0)
        self.game.cycle_cell_image(0, 3)
        self.assertEqual(self.game.count_remaining_mine(), -1)
    
    def test_count_flagged_mine(self):
        self.assertEqual(self.game.count_flagged_mine(), 0)
        self.game.cycle_cell_image(0, 0)
        self.game.cycle_cell_image(1, 1)
        self.assertEqual(self.game.count_flagged_mine(), 2)
        self.game.cycle_cell_image(0, 0)
        self.assertEqual(self.game.count_flagged_mine(), 1)
    
    def test_check_finished(self):
        self.assertEqual(self.game.check_finished(), False)
        self.assertEqual(self.game.open_cell_adjacent(4, 1), False)
        self.assertEqual(self.game.open_cell_adjacent(5, 1), False)
        self.assertEqual(self.game.open_cell_adjacent(5, 2), False)
        for i in [3, 4]:
            for j in [0, 1, 2, 3]:
                self.assertEqual(self.game.open_cell(i, j), False)
        self.assertEqual(self.game.check_finished(), False)
        self.assertEqual(self.game.open_cell_adjacent(0, 1), False)
        self.assertEqual(self.game.open_cell_adjacent(0, 2), False)
        self.assertEqual(self.game.open_cell_adjacent(1, 0), False)
        self.assertEqual(self.game.open_cell_adjacent(2, 0), False)
        self.assertEqual(self.game.open_cell_adjacent(2, 1), False)
        self.assertEqual(self.game.check_finished(), False)
        self.assertEqual(self.game.open_cell_adjacent(1, 2), False)
        self.assertEqual(self.game.check_finished(), True)
    
    def test_get_cell_text(self):
        self.assertEqual(self.game.get_cell_text(0, 0), None)
        self.assertEqual(self.game.get_cell_text(0, 1), None)
        
        self.game.open_cell(0, 1)
        self.game.open_cell_adjacent(4, 1)
        self.assertEqual(self.game.get_cell_text(0, 1), 2)
        self.assertEqual(self.game.get_cell_text(0, 2), 1)
        self.assertEqual(self.game.get_cell_text(0, 3), 0)
        
        self.assertEqual(self.game.get_cell_text(1, 0), 2)
        self.assertEqual(self.game.get_cell_text(2, 0), 1)
        self.assertEqual(self.game.get_cell_text(3, 0), 0)
        
        self.assertEqual(self.game.get_cell_text(1, 1), 3)
    
    def test_count_adjacent_mine(self):
        self.game.mines[4][6] = True
        
        self.assertEqual(self.game.count_adjacent_mine(1, 1), 3)
        self.assertEqual(self.game.count_adjacent_mine(0, 0), 2)
        self.assertEqual(self.game.count_adjacent_mine(2, 2), 2)
        self.assertEqual(self.game.count_adjacent_mine(3, 0), 0)
        self.assertEqual(self.game.count_adjacent_mine(6, 4), 1)
        self.assertEqual(self.game.count_adjacent_mine(5, 4), 1)
        self.assertEqual(self.game.count_adjacent_mine(6, 3), 1)
    
    def test_iter_empty_adjacent(self):
        self.game.mines[3][2] = True
        self.game.mines[4][2] = True
        self.game.mines[2][4] = True
        self.game.mines[2][5] = True
        self.game.mines[2][6] = True
        
        self.assertEqual(sum([1 for x in self.game.iter_empty_adjacent(0, 2)]), 1)
        self.assertEqual(sum([1 for x in self.game.iter_empty_adjacent(0, 3)]), 6)
        self.assertEqual(sum([1 for x in self.game.iter_empty_adjacent(0, 0)]), 1)
        self.assertEqual(sum([1 for x in self.game.iter_empty_adjacent(2, 0)]), 1)
        self.assertEqual(sum([1 for x in self.game.iter_empty_adjacent(3, 0)]), 10)
        self.assertEqual(sum([1 for x in self.game.iter_empty_adjacent(6, 4)]), 8)
    

if __name__ == '__main__':
    unittest.main()
