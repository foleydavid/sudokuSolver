

# BRAIN CLASS FOR SOLVING SUDOKU
class Brain:

    # INITIAL SETUP
    def __init__(self, grid):

        # CREATE INTERNAL COPY OF VARIABLE GRID
        self.grid = []
        for i in range(9):
            self.grid.append([])
            for j in range(9):
                self.grid[i].append(grid[i][j])

    # CHANGE GRID VALUES
    def update_grid(self, grid):

        self.grid = []
        for i in range(9):
            self.grid.append([])
            for j in range(9):
                self.grid[i].append(grid[i][j])

    # EVALUATE SUDOKU BOARD AS CORRECT OR INCORRECT
    def eval(self):

        if self.rows_pass() and self.cols_pass() and self.quads_pass():
            return True
        return False

    # CHECK FOR ERRORS WITHIN EACH ROW
    def rows_pass(self):

        for row in self.grid:
            so_far = [""]
            for col in row:
                if col in so_far or col > 9:
                    return False
                so_far.append(col)
        return True

    # CHECK FOR ERRORS WITHIN EACH COLUMN
    def cols_pass(self):
        for col_id in range(9):
            so_far = [""]
            for row_id in range(9):
                val = self.grid[row_id][col_id]
                if val in so_far or val > 9:
                    return False
                so_far.append(val)
        return True

    # CHECK FOR ERRORS WITHIN EACH SECTION / "QUADRANT"
    def quads_pass(self):

        # CREATE ARRAY OF UPPER LEFT STARTING INDEX
        starts = [
            [0, 0], [0, 3], [0, 6],
            [3, 0], [3, 3], [3, 6],
            [6, 0], [6, 3], [6, 6]
        ]

        # SEARCH THROUGH EACH SECTION
        for start in starts:
            so_far = [""]
            for i in range(3):
                for j in range(3):
                    val = self.grid[start[0]+i][start[1]+j]
                    if val in so_far or val > 9:
                        return False
                    so_far.append(val)
        return True

    # FIND X, Y POSITION OF NEXT EMPTY SUDOKU SLOT
    @staticmethod
    def find_empty(board):
        # return (val, val)
        for row_num, row in enumerate(board):
            for col_num, val in enumerate(row):
                if val == 0:
                    return row_num, col_num
        return None

    # GIVEN POSITION - EVALUATE ROW, COLUMN, SECTION FOR CORRECTNESS
    @staticmethod
    def is_valid(board, row_num, col_num, num):

        # CHECK CURRENT ROW
        for col, val in enumerate(board[row_num]):
            if val == num and col != col_num:
                return False

        # CHECK CURRENT COLUMN
        for row in range(len(board)):
            if board[row][col_num] == num and row != row_num:
                return False

        # CHECK CURRENT SECTION
        x_sect = col_num // 3
        y_sect = row_num // 3
        for i in range(x_sect * 3, x_sect * 3 + 3):
            for j in range(y_sect * 3, y_sect * 3 + 3):
                if board[j][i] == num and (j != row_num or i != col_num):
                    return False

        return True

    # AUTO-SOLVE SUDOKU BOARD USING BACKTRACKING
    def solve(self):

        # ACQUIRE NEXT EMPTY POSITION
        next_pos = Brain.find_empty(self.grid)

        # RETURN TRUE / FINISHED IF NO MORE POSITIONS TO EVALUATE
        if not next_pos:
            return True

        # STORE NEXT POSITION IN ROW, COLUMN FORM
        else:
            row, col = next_pos

        # CHECK POSITION VALUE CORRECTNESS FOR NUMS 1-9
        for i in range(1, 10):

            # CHECK BOARD VALIDITY WITH NEW 1-9 VALUE
            if self.is_valid(self.grid, row, col, i):
                self.grid[row][col] = i

                # REPEAT PROCESS
                # CHECK FOR CORRECTNESS UNTIL BOARD FILLED
                if self.solve():
                    return True

                # CLEAR POSITION VALUE
                # CANNOT BE SOLVED WITH PREVIOUS VALUES ENTERED
                self.grid[row][col] = 0

        # COULD NOT BE SOLVED - ADJUST PREVIOUS VALUES
        return False
