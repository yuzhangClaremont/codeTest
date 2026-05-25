# Coding Quiz Answers

# Add your quiz solutions here


def reverse_list(l: list):
    """
    Reverse a list without using any built-in functions.
    The function should return a reversed list.
    Input l is a list that may contain any type of data.
    """
    result = l[:]
    left = 0
    right = len(result) - 1
    
    while left < right:
        result[left], result[right] = result[right], result[left]
        left += 1
        right -= 1
    
    return result
 
def solve_sudoku(matrix):
    """
    Write a program to solve a 9x9 Sudoku board.
    The board must be completed so that every row, column, and 3x3 section
    contains all digits from 1 to 9.
    Input: a 9x9 matrix representing the board.
    """
    def is_valid(board, row, col, num):
        for i in range(9):
            if board[row][i] == num:
                return False
        for i in range(9):
            if board[i][col] == num:
                return False
        start_row = (row // 3) * 3
        start_col = (col // 3) * 3
        for i in range(3):
            for j in range(3):
                if board[start_row + i][start_col + j] == num:
                    return False
        return True
    
    def solve(board):
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    for num in range(1, 10):
                        if is_valid(board, row, col, num):
                            board[row][col] = num
                            if solve(board):
                                return True
                            board[row][col] = 0
                    return False
        return True
    
    solve(matrix)
    return matrix