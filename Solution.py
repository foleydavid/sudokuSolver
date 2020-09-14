my_board = [
    [0,0,5,  0,0,0,  0,0,0],
    [0,0,2,  4,0,1,  0,7,0],
    [3,0,4,  0,0,0,  5,6,0],

    [0,0,0,  0,0,0,  0,0,0],
    [0,0,0,  0,0,7,  9,8,4],
    [8,0,0,  0,9,0,  0,1,0],

    [0,0,0,  2,0,0,  1,0,0],
    [0,9,0,  0,7,0,  0,0,2],
    [0,1,8,  3,0,0,  0,4,0]
]

def printBoard(board):

    print("- - - - - - - - - - -")
    for row_num, row in enumerate(board):
        if row_num % 3 == 0 and row_num != 0:
            print("")

        for col_num, val in enumerate(row):
            if col_num % 3 == 0 and col_num != 0:
                print("  ", end = "")
            print(str(val) + " ", end = "")

        print("")
    print("- - - - - - - - - - -")
    print("")

def findEmpty(board):
    #return (val, val)
    for row_num, row in enumerate(board):
        for col_num, val in enumerate(row):
            if val == 0:
                return row_num, col_num

    return None

def isValid(board, row_num, col_num, num):

    #check current row
    for col, val in enumerate(board[row_num]):
        if val == num:
            return False

    #check current col
    for row in range(len(board)):
        if board[row][col_num] == num:
            return False

    #check sq section
    x_sect = col_num // 3
    y_sect = row_num // 3
    for i in range(x_sect * 3, x_sect * 3 + 3):
        for j in range(y_sect * 3, y_sect * 3 + 3):
            if board[j][i] == num:
                return False

    return True

def solve(board):
    next_pos = findEmpty(board)

    #if filled up, return TRUE/solution found
    #base case of recursion
    if not next_pos:
        return True

    #sudoku not filled up yet
    else:
        row, col = next_pos

    #loop through all values for next position
    for i in range(1, 10):
        #board is valid with given number, assign it
        if isValid(board, row, col, i):
            board[row][col] = i

            #if you can solve it forward, exit with True
            if solve(board):
                return True

            #didnt solve with that assignment, try for a new value "i"
            board[row][col] = 0

    #not able to solve based on all prior entries
    return False

#call functions
solve(my_board)
printBoard(my_board)
