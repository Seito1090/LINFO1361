from pycsp3 import *

# Definition of the initial sudoku grid
clues = [[0, 2, 0, 5, 0, 1, 0, 9, 0],
         [8, 0, 0, 2, 0, 3, 0, 0, 6],
         [0, 3, 0, 0, 6, 0, 0, 7, 0],
         [0, 0, 1, 0, 0, 0, 6, 0, 0],
         [5, 4, 0, 0, 0, 0, 0, 1, 9],
         [0, 0, 2, 0, 0, 0, 7, 0, 0],
         [0, 9, 0, 0, 3, 0, 0, 8, 0],
         [2, 0, 0, 8, 0, 4, 0, 0, 7],
         [0, 1, 0, 9, 0, 7, 0, 6, 0]]

# x[i][j] is the value at row i and col j
x = VarArray(size=[9, 9], dom=range(1, 10))

satisfy(
   # constraints 1
   [AllDifferent(x[i]) for i in range(9)],

   # constraints 2
   [AllDifferent(x[:, j]) for j in range(9)],

   # constraints 3
   [AllDifferent(x[i:i + 3, j:j + 3]) for i in [0, 3, 6] for j in [0, 3, 6]],

   # constraints 4
   [x[i][j] == clues[i][j] for i in range(9) for j in range(9) if clues and clues[i][j] > 0]
)

# Solve the problem and print the solution if found
if solve(solver=CHOCO) is SAT:
    print("SATISFIABLE")
    print(values(x))
else:
    print("UNSATISFIABLE")