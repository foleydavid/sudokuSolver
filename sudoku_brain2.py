class Brain:
    def __init__(self, grid):
        #must be done this way, because lists are mutable
        #if set equal the parent will change with adjustments
        self.grid = []
        for i in range(9):
            self.grid.append([])
            for j in range(9):
                self.grid[i].append(grid[i][j])

    def update_grid(self, grid):
        self.grid = []
        for i in range(9):
            self.grid.append([])
            for j in range(9):
                self.grid[i].append(grid[i][j])

    def eval(self):
        if self.rows_pass() and self.cols_pass() and self.quads_pass():
            return True
        return False

    def rows_pass(self):
        for row in self.grid:
            so_far = [""]
            for col in row:
                if col in so_far or col > 9:
                    return False
                so_far.append(col)
        return True

    def cols_pass(self):
        for col_id in range(9):
            so_far = [""]
            for row_id in range(9):
                val = self.grid[row_id][col_id]
                if val in so_far or val > 9:
                    return False
                so_far.append(val)
        return True

    def quads_pass(self):
        starts = [
            [0, 0], [0, 3], [0, 6],
            [3, 0], [3, 3], [3, 6],
            [6, 0], [6, 3], [6, 6]
        ]
        for start in starts:
            so_far = [""]
            for i in range(3):
                for j in range(3):
                    val = self.grid[start[0]+i][start[1]+j]
                    if val in so_far or val > 9:
                        return False
                    so_far.append(val)
        return True

    @staticmethod
    def findEmpty(board):
        # return (val, val)
        for row_num, row in enumerate(board):
            for col_num, val in enumerate(row):
                if val == 0:
                    return row_num, col_num
        return None

    @staticmethod
    def is_valid(board, row_num, col_num, num):

        # check current row
        for col, val in enumerate(board[row_num]):
            if val == num:
                return False

        # check current col
        for row in range(len(board)):
            if board[row][col_num] == num:
                return False

        # check sq section
        x_sect = col_num // 3
        y_sect = row_num // 3
        for i in range(x_sect * 3, x_sect * 3 + 3):
            for j in range(y_sect * 3, y_sect * 3 + 3):
                if board[j][i] == num:
                    return False

        return True

    def solve(self):
        next_pos = Brain.findEmpty(self.grid)

        # if filled up, return TRUE solution found
        # base case of recurssion
        if not next_pos:
            return True

        # not filled up yet
        else:
            row, col = next_pos

        # loop through all values
        for i in range(1, 10):
            # if board if valid with given number, assign it
            # may be able to go back and change notes since board not changed yet...
            if self.is_valid(self.grid, row, col, i):
                self.grid[row][col] = i

                # if you can solve it forward, exit with True
                if self.solve():
                    return True

                # didnt solve with that assignment, try for a new value "i"
                self.grid[row][col] = 0

        # makes it here, then it has not been solved
        return False
