import unittest
from Solution import Solution

class TestSolution(unittest.TestCase):
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

    def setUp(self):
        self.ex_1 = Solution(TestSolution.my_board)
        self.ex_2 = Solution(TestSolution.next_board)

    def test_findEmpty(self):
        self.assertEqual(self.ex_1.findEmpty(self.ex_1.board), (0, 0))
        self.assertEqual(self.ex_2.findEmpty(self.ex_2.board), (0, 0))

    def test_isValid(self):
        self.assertTrue(Solution.isValid(self.ex_1.board, 0, 0, 1))
        self.assertFalse(Solution.isValid(self.ex_1.board, 8, 8, 4))
        self.assertTrue(Solution.isValid(self.ex_2.board, 3, 2, 8))
        self.assertFalse(Solution.isValid(self.ex_2.board, 8, 8, 6))

    def test_solve(self):
        self.assertTrue(self.ex_1.solve(self.ex_1.board))
        self.assertTrue(self.ex_2.solve(self.ex_2.board))

        for i, row in enumerate(self.ex_1.board):
            for j, val in enumerate(row):
                self.assertTrue(Solution.isValid(self.ex_1.board, i, j, self.ex_1.board[i][j]))

        for i, row in enumerate(self.ex_2.board):
            for j, val in enumerate(row):
                self.assertTrue(Solution.isValid(self.ex_2.board, i, j, self.ex_2.board[i][j]))

if __name__ == "__main__":
    unittest.main()

