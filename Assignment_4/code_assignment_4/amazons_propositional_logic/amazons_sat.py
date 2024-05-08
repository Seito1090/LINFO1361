from clause import *

"""
For the n-amazon problem, the only code you have to do is in this file.

You should replace

# your code here

by a code generating a list of clauses modeling the n-amazons problem
for the input file.

You should build clauses using the Clause class defined in clause.py

Here is an example presenting how to create a clause:
Let's assume that the length/width of the chessboard is 4.
To create a clause X_0_1 OR ~X_1_2 OR X_3_3
you can do:

clause = Clause(4)
clause.add_positive(0, 1)
clause.add_negative(1, 2)
clause.add_positive(3, 3)

The clause must be initialized with the length/width of the chessboard.
The reason is that we use a 2D index for our variables but the format
imposed by MiniSAT requires a 1D index.
The Clause class automatically handle this change of index, but needs to know the
number of column and row in the chessboard.

X_0_0 is the literal representing the top left corner of the chessboard
"""

def get_init_clauses(size, placed_amazons):
    clauses = []
    for x, y in placed_amazons: # Add clauses to ensure that the already placed amazons stay in the same positions
        clause = Clause(size)
        clause.add_positive(x, y)
        clauses.append(clause)
    clauses.extend(get_init_neg_clauses(size, placed_amazons)) # Add clauses to ensure that the already placed amazons influence the positions of the other amazons
    return clauses

def get_init_neg_clauses(size, placed_amazons):
    clauses = []
    for a,b in placed_amazons:
        clause = Clause(size)
        for x in range(size):
            for y in range(size):
                if (x == a or y == b): # Check lines and columns
                    clause.add_negative(x, y)
                elif abs(x - a) == abs(y - b): # Check diagonals
                    clause.add_negative(x, y)
                elif abs(x - a) == 2 and abs(y - b) == 3 or (abs(x - a) == 3 and abs(y - b) == 2): # Check 3-2 moves
                    clause.add_negative(x, y)
                elif abs(x - a) == 1 and abs(y - b) == 4 or (abs(x - a) == 4 and abs(y - b) == 1): # Check 4-1 moves
                    clause.add_negative(x, y)
        clauses.append(clause)
    return clauses

def get_extended_negclauses(size): # The name says it all
    four_by_one_moves = [(4,1), (1,4), (-4,-1), (-1,-4), (4,-1), (1,-4), (-4,1), (-1,4)]
    three_by_two_moves = [(3,2), (2,3), (-3,-2), (-2,-3), (3,-2), (2,-3), (-3,2), (-2,3)]
    clauses = []
    for a,b in four_by_one_moves:
        for x in range(size):
            for y in range(size):
                if 0 <= x + a < size and 0 <= y + b < size:
                    clause = Clause(size)
                    clause.add_negative(x, y)
                    clause.add_negative(x + a, y + b)
                    clauses.append(clause)
    for a,b in three_by_two_moves:
        for x in range(size):
            for y in range(size):
                if 0 <= x + a < size and 0 <= y + b < size:
                    clause = Clause(size)
                    clause.add_negative(x, y)
                    clause.add_negative(x + a, y + b)
                    clauses.append(clause)
    return clauses

def get_expression(size: int, placed_amazons: list[(int, int)]) -> list[Clause]:
    """
    Defines the clauses for the N-amazons problem
    :param size: length/width of the chessboard
    :param placed_amazons: a list of the already placed amazons
    :return: a list of clauses
    """ 

    # Init the clauses, positives to ensure the already placed amazons stay in the same positions, negatives to ensure they influence the positions of the other amazons
    expression = get_init_clauses(size, placed_amazons) 
    
    ### Adding clauses to block invalid moves for the amazons ###

    # At least one amazon has to be in a row
    for x in range(size):
        clause = Clause(size)
        for y in range(size):
            clause.add_positive(x, y)
        expression.append(clause)  

    # At least one amazon has to be in a column 
    for y in range(size):
        clause = Clause(size)
        for x in range(size):
            clause.add_positive(x, y)
        expression.append(clause)  

    # At most one amazon per row
    diagonals = []
    for i in range(size):
        for j in range(size):
            diag = []
            diag_inv = []
            for d in range(size):
                if (i == 0 or j == 0) and j + d < size and i + d < size:
                    diag.append((i + d, j + d))
                if (j == 0 or i == size-1) and j + d < size and i - d >= 0:
                    diag_inv.append((i - d, j + d))
            if diag != []:
                diagonals.append(diag)
            if diag_inv != []:
                diagonals.append(diag_inv)

    # Create diagonal clauses 
    for diag in diagonals:
        for x in range(len(diag)):
            for y in range(x + 1, len(diag)):
                clause = Clause(size)
                clause.add_negative(diag[x][0], diag[x][1])
                clause.add_negative(diag[y][0], diag[y][1])
                expression.append(clause)
 
    # At most one amazon per row
    for x in range(size):
        for y in range(size):
            for z in range(y + 1, size):
                clause = Clause(size)
                clause.add_negative(x, y)
                clause.add_negative(x, z)
                expression.append(clause)

    # At most one amazon per column
    for j in range(size):
        for i in range(size):
            for k in range(i + 1, size):
                clause = Clause(size)
                clause.add_negative(i, j)
                clause.add_negative(k, j)
                expression.append(clause)

    # At most one amazon in each extended move
    expression.extend(get_extended_negclauses(size))

    return expression
