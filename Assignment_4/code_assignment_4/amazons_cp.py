import sys
from pycsp3 import *


def read_instance(filename: str) -> (int, list[(int, int)]):
    """
    Read the given instance file
    :param filename: the path to the instance file
    :return: a tuple containing the length/width of the chessboard and a list
    of (i, j) tuples containing the position of the forced amazons where i is the row index and j is the column index
    """
    with open(filename, 'r') as file:
        lines = file.readlines()
    size, placed_amazon_nbr = [int(x) for x in lines[0].strip().split(" ")]
    placed_amazons = []
    for i in range(1, placed_amazon_nbr + 1):
        column, row = [int(x) for x in lines[i].strip().split(" ")]
        placed_amazons.append((column, row))
    return size, placed_amazons


def verify_line(line: list[int]) -> bool:
    """
    Check that a line contains at most one amazon
    :param line: the line to check
    :return: True iff the line contains at most one amazon
    """
    has_amazon = False
    for i in range(len(line)):
        if has_amazon and line[i] == 1:
            return False
        if not has_amazon and line[i] == 1:
            has_amazon = True
    return True


def verify_diagonals(grid : list[list[int]], index_ref: (int, int)) -> bool:
    """
    Check that an amazon has no conflict with another amazon on its diagonal
    :param grid: the solution
    :param index_ref: the position of the amazon
    :return: True iff there is no other amazon on the diagonal
    """
    for i in range(1, len(grid)):
        if index_ref[0] - i >= 0 and index_ref[1] - i >= 0:
            if grid[index_ref[0] - i][index_ref[1] - i] == 1:
                return False

        if index_ref[0] + i < len(grid) and index_ref[1] - i >= 0:
            if grid[index_ref[0] + i][index_ref[1] - i] == 1:
                return False

        if index_ref[0] - i >= 0 and index_ref[1] + i < len(grid):
            if grid[index_ref[0] - i][index_ref[1] + i] == 1:
                return False

        if index_ref[0] + i < len(grid) and index_ref[1] + i < len(grid):
            if grid[index_ref[0] + i][index_ref[1] + i] == 1:
                return False
    return True


def verify_3_2_moves(grid : list[list[int]], index_ref: (int, int)) -> bool:
    """
    Check that an amazon has no conflict with another amazon on its 3x2 moves
    :param grid: the solution
    :param index_ref: the position of the amazon
    :return: True iff there is no other amazon on the diagonal
    """
    valid = True
    tests = [(index_ref[0] - 3, index_ref[1] - 2),
             (index_ref[0] - 3, index_ref[1] + 2),
             (index_ref[0] + 3, index_ref[1] - 2),
             (index_ref[0] + 3, index_ref[1] + 2),
             (index_ref[0] - 2, index_ref[1] - 3),
             (index_ref[0] - 2, index_ref[1] + 3),
             (index_ref[0] + 2, index_ref[1] - 3),
             (index_ref[0] + 2, index_ref[1] + 3)]

    for test in tests:
        if 0 <= test[0] < len(grid) and 0 <= test[1] < len(grid):
            if grid[test[0]][test[1]] == 1:
                print("3x2 conflict between ({}, {}) and ({}, {})".format(index_ref[0], index_ref[1], test[0], test[1]))
                valid = False

    return valid


def verify_4_1_moves(grid: list[list[int]], index_ref: (int, int)) -> bool:
    """
    Check that an amazon has no conflict with another amazon on its 4x1 moves
    :param grid: the solution
    :param index_ref: the position of the amazon
    :return: True iff there is no other amazon on the diagonal
    """
    valid = True
    tests = [(index_ref[0] - 4, index_ref[1] - 1),
             (index_ref[0] - 4, index_ref[1] + 1),
             (index_ref[0] + 4, index_ref[1] - 1),
             (index_ref[0] + 4, index_ref[1] + 1),
             (index_ref[0] - 1, index_ref[1] - 4),
             (index_ref[0] - 1, index_ref[1] + 4),
             (index_ref[0] + 1, index_ref[1] - 4),
             (index_ref[0] + 1, index_ref[1] + 4)]

    for test in tests:
        if 0 <= test[0] < len(grid) and 0 <= test[1] < len(grid):
            if grid[test[0]][test[1]] == 1:
                print("4x1 conflict between ({}, {}) and ({}, {})".format(index_ref[0], index_ref[1], test[0], test[1]))
                valid = False
    return valid


def verify_n_amazons(grid : list[list[int]], placed_amazons):
    """
    Check the validity of the solution
    :param grid: the solution to check
    :param placed_amazons: the set of placed amazons defined by the instance
    :return: True iff the solution is valid
    """
    valid = True

    for amazon in placed_amazons:
        if grid[amazon[0]][amazon[1]] != 1:
            valid = False
            print("Forced amazon at position ({}, {}) is missing".format(amazon[0], amazon[1]))

    for i in range(len(grid)):
        line = grid[i]
        if not verify_line(line):
            valid = False
            print("Line {} contains several amazons".format(i))

        column = [grid[j][i] for j in range(len(grid))]
        if not verify_line(column):
            valid = False
            print("Column {} contains several amazons".format(i))

    nbr_amazons = 0
    for i in range(len(grid)):
        for j in range(len(grid)):
            if grid[i][j] == 1:
                nbr_amazons += 1

                if not verify_diagonals(grid, (i, j)):
                    valid = False
                    print("Diagonals of amazon at position ({}, {}) contains other amazons".format(i, j))
                if not verify_3_2_moves(grid, (i, j)):
                    valid = False
                if not verify_4_1_moves(grid, (i, j)):
                    valid = False

    if nbr_amazons < len(grid):
        valid = False
        print("Some amazons are missing")

    if nbr_amazons > len(grid):
        valid = False
        print("There are too many amazons")

    return valid


def amazons_cp(size: int, placed_amazons: list[(int, int)]) -> (bool, list[list[int]]):
    """
    Solve the N-Amazon problem using Constraint Programming
    :param size: the width/length of the chessboard
    :param placed_amazons: a list of the already placed amazons represented by a tuple (row, column)
    :return: a tuple (SAT, output) where SAT is true iff the model is satisfiable
    and output is 2D grid representing the solution: output[i][j] == 1 iff there is an amazon at row i and column j
    otherwise output[i][j] == 0
    """

    # Create the variables here
    # Array of positions of the amazons
    amazons = VarArray(size=size, dom=range(size))

    # Function that defines the circle of radius 3.2 to 4.8 around a position (x, y)
    circle_function = lambda i,j, x,y: (((i - x)**2 + (j - y)**2) > 10) * (((i - x)**2 + (j - y)**2) < 18)
    # Precompute the values for the X coordinates
    circle_buffer = [lambda j,y: circle_function(i, j, x, y) for x in range(size) for i in range(size)]
    satisfy(
        # Write your constraints here
        # Already placed amazons
        [amazons[x] == y for x, y in placed_amazons],
        # Each line and column must contain at most one amazon
        AllDifferent(amazons),
        # Each diagonal must contain at most one amazon
        [Sum([abs(i - j) == abs(amazons[i] - amazons[j]) for j in range(size)]) <= 1 for i in range(size)],   
        # Each 3x2 and 4x1 moves must NEVER contain an amazon
        [Sum([
            circle_function(i, amazons[i], x, y) for x,y in [(j, amazons[j]) for j in range(size)]
        ]) == 0 for i in range(size)]
     )

    if False:     
        # representation of the last constrain
        num_boards = 6
        for b in range(0, size*size, num_boards):
            for i in range(size):
                for x in range(b, min(b + num_boards, size*size)):
                    y, x = divmod(x, size)
                    for j in range(size):
                        if circle_function(i, j, x, y):
                            print('🔴', end="")
                        elif abs(i - x) == abs(j - y):
                            print('🔵', end="")
                        elif i == x or j == y:
                            print('🟢', end="")
                        else:
                            print('⬜', end="")
                    print(" ", end="")  # print a space between boards
                print()  # print a newline after each row of boards
            print()  # print a newline after each set of 4 boards

    # output[i][j] == 1 iff there is an amazon at row i and column j
    # otherwise output[i][j] == 0
    output = [[0 for _ in range(size)] for _ in range(size)]

    # Solve the model and retrieve the solution
    if solve(solver=CHOCO) is SAT:
        status = True
        # Fill the output grid with solution
        for i in range(size):
            output[i][amazons[i].value] = 1
    else:
        status = False

    if False:
        for i in range(size):
            for j in range(size):
                if output[i][j] == 1:
                    print("👑", end="")
                else:
                    print("⬜", end="")
            print()

    # Do not remove this line ! Otherwise, errors will occur during 
    # the evaluation runned by Inginious
    clear()

    # Do not change the output or Inginious will crash
    return status, output


if __name__ == '__main__':
    instance_file = sys.argv[1]
    size, placed_amazons = read_instance(instance_file)
    status, solution = amazons_cp(size, placed_amazons)
    if status:
        print("Solution found")
        for line in solution:
            print(line)
        verify_n_amazons(solution, placed_amazons)
    else:
        print("No solution found")
