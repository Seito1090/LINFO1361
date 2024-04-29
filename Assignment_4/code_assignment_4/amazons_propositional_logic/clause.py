"""
Class used to represent a clause in CNF for the n-amazons problem.

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
"""


class Clause:

    def __init__(self, size: int, varname='X'):
        """
        Initialize an empty clause
        :param size: the length/width of the chessboard
        :param varname: the name of the variable
        """
        self.varname = varname
        self.n_rows = self.n_columns = size
        self.value = []

    def index(self, row_ind: int, column_ind: int) -> int:
        """
        Convert the 2D index of a variable to its corresponding 1D index
        :param row_ind: the row index of the variable
        :param column_ind: the column index of the variable
        :return: the 1D index
        """
        if 0 <= row_ind < self.n_rows and 0 <= column_ind < self.n_columns:
            return row_ind * self.n_columns + column_ind
        else:
            raise ValueError("Indices : row_ind =", row_ind, "column_ind =", column_ind, "are incorrect")

    def str_from_index(self, index: int) -> str:
        """
        Convert the 1D index of a variable to its 2D version, and return a string composed of the variable name
        and the 2D indexes
        :param index: the 1D index of the variable
        :return: a string of the complete variable name
        """
        if index >= 0:
            index -= 1
        else:
            index += 1
        row_ind, column_ind = divmod(abs(index), self.n_columns)

        if index < 0:
            return '~{0}_{1}_{2}'.format(self.varname, row_ind, column_ind)
        return '{0}_{1}_{2}'.format(self.varname, row_ind, column_ind)

    def add_positive(self, row_ind: int, column_ind: int):
        """
        Add a positive literal to the clause
        :param row_ind: the row index of the variable
        :param column_ind: the column index of the variable
        """
        self.value.append(self.index(row_ind, column_ind)+1)

    def add_negative(self, row_ind: int, column_ind: int):
        """
        Add a negative literal to the clause
        :param row_ind: the row index of the variable
        :param column_ind: the column index of the variable
        """
        self.value.append(-self.index(row_ind, column_ind)-1)

    def minisat_str(self) -> str:
        return ' '.join([str(x) for x in self.value])

    def __str__(self):
        return ' or '.join([self.str_from_index(x) for x in self.value])
