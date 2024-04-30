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
    # Matrix of size x size variables, where each value is 0 or 1
    amazons = VarArray(size=(2, size), dom=range(size))

    # Collapse the already placed amazons
    for id, amazon in enumerate(placed_amazons):
        amazons[0][id].value = amazon[0]
        amazons[1][id].value = amazon[1]

    scale = 100

    satisfy(
        # Write your constraints here
        # ROWS
        # Queen_X_i != queen_X_j
        AllDifferent(amazons[0]),
        # COLUMNS
        # Queen_Y_i != queen_Y_j
        AllDifferent(amazons[1]),
        # DIAGONALS
        # abs(Queen_X_i - Queen_X_j) != abs(Queen_Y_i  - Queen_Y_j)
        [abs(amazons[0][i] - amazons[0][j]) != abs(amazons[1][i] - amazons[1][j]) for i in range(size) for j in range(size) if i != j],
        # CIRCLE
        # (Queen_X_i - Queen_X_j)^2 + (Queen_Y_i - Queen_Y_j)^2 < 3.5^2 and > 4.2^2
        [Or(scale*((amazons[0][i] - amazons[0][j]) ** 2 + (amazons[1][i] - amazons[1][j]) ** 2) < int(scale*(3.5**2)), 
            scale*((amazons[0][i] - amazons[0][j]) ** 2 + (amazons[1][i] - amazons[1][j]) ** 2) > int(scale*(4.2**2))) for i in range(size) for j in range(size) if i != j]
    )

    # output[i][j] == 1 iff there is an amazon at row i and column j
    # otherwise output[i][j] == 0
    output = [[0 for _ in range(size)] for _ in range(size)]

    # Solve the model and retrieve the solution
    if solve(solver=CHOCO) is SAT:
        status = True
        # Fill the output grid with solution
        for i in range(size):
            output[amazons[0][i].value()][amazons[1][i].value()] = 1
    else:
        status = False

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
