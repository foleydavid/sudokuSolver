import unittest
from sudoku_brain2 import Brain


# TEST SUDOKU_BRAIN CLASS FOR CALCULATIONS
class TestSolution(unittest.TestCase):

    # EXAMPLE ONE SUDOKU BOARD
    my_board = [
        [0, 0, 5, 0, 0, 0, 0, 0, 0],
        [0, 0, 2, 4, 0, 1, 0, 7, 0],
        [3, 0, 4, 0, 0, 0, 5, 6, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 7, 9, 8, 4],
        [8, 0, 0, 0, 9, 0, 0, 1, 0],
        [0, 0, 0, 2, 0, 0, 1, 0, 0],
        [0, 9, 0, 0, 7, 0, 0, 0, 2],
        [0, 1, 8, 3, 0, 0, 0, 4, 0]
    ]

    # EXAMPLE TWO SUDOKU BOARD
    next_board = [
        [0, 0, 0, 0, 0, 0, 0, 3, 0],
        [0, 6, 2, 0, 0, 4, 0, 0, 8],
        [5, 0, 0, 0, 0, 0, 7, 0, 0],
        [9, 1, 0, 5, 0, 0, 0, 0, 7],
        [0, 5, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 7, 0, 4, 2, 0, 0, 0],
        [0, 0, 1, 0, 7, 0, 0, 0, 6],
        [0, 0, 0, 9, 0, 6, 8, 0, 0],
        [7, 0, 0, 0, 5, 0, 0, 0, 0]
    ]

    # SETUP BOARD OBJECT BEFORE EACH TEST
    def setUp(self):
        self.ex_1 = Brain(TestSolution.my_board)
        self.ex_2 = Brain(TestSolution.next_board)

    # TEST FIND_EMPTY FUNCTION CALL
    def test_find_empty(self):
        self.assertEqual(self.ex_1.find_empty(self.ex_1.grid), (0, 0))
        self.assertEqual(self.ex_2.find_empty(self.ex_2.grid), (0, 0))

    # TEST IS_VALID FUNCTION CALL
    def test_is_valid(self):
        self.assertTrue(Brain.is_valid(self.ex_1.grid, 0, 0, 1))
        self.assertFalse(Brain.is_valid(self.ex_1.grid, 8, 8, 4))
        self.assertTrue(Brain.is_valid(self.ex_2.grid, 3, 2, 8))
        self.assertFalse(Brain.is_valid(self.ex_2.grid, 8, 8, 6))

    # TEST SOLVE FUNCTION CALL
    def test_solve(self):

        # SOLVE EXAMPLE 1 AND EXAMPLE 2 OBJECTS
        self.assertTrue(self.ex_1.solve())
        self.assertTrue(self.ex_2.solve())

        # EXAMPLE 1 - CHECK IF EACH BOX IS VALID
        for i, row in enumerate(self.ex_1.grid):
            for j, val in enumerate(row):
                self.assertTrue(Brain.is_valid(self.ex_1.grid, i, j,
                                               self.ex_1.grid[i][j]))

        # EXAMPLE 2 - CHECK IF EACH BOX IS VALID
        for i, row in enumerate(self.ex_2.grid):
            for j, val in enumerate(row):
                self.assertTrue(Brain.is_valid(self.ex_2.grid, i, j,
                                               self.ex_2.grid[i][j]))


# RUN TESTS FROM DIRECT ONLY
if __name__ == "__main__":
    unittest.main()
