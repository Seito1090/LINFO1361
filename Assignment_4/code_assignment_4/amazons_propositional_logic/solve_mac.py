#!/usr/bin/env python3
import sys
from amazons_sat import get_expression
import minisat


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


def get_val_from_index(index: int, size: int) -> (int, int):
    """
    Utility function to retrieve the positions of the amazons from the set of literal returned as a solution by MiniSAT
    :param index: the index of the literal in the MiniSAT solution
    :param size: the length/width of the chessboard
    :return: a tuple (i, j) representing the position of the amazon where i is the row index and j is the column index
    """
    index -= 1
    row_ind, column_ind = divmod(index, size)
    return row_ind, column_ind


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:", sys.argv[0], "INSTANCE_FILE", file=sys.stderr)
        exit(1)

    size, fixed_amazons = read_instance(sys.argv[1])
    n_rows = n_columns = size
    expression = get_expression(size, fixed_amazons)
    nb_vars = n_rows * n_columns
    is_sat, solution = minisat.minisat(nb_vars, [clause.minisat_str() for clause in expression], './minisatMac')

    if not is_sat:
        print("The problem is UNSAT")
        exit(0)
    print("The problem is SAT")
    print("Solution : ")
    grid = [[0 for _ in range(size)] for _ in range(size)]
    for s in solution:
        row, column = get_val_from_index(s, size)
        grid[row][column] = 1

    for row in grid:
        print(row)

    valid = verify_n_amazons(grid, fixed_amazons)
    if not valid:
        print("The solution is not valid")

