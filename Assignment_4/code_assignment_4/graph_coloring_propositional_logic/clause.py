"""
Class used to represent a clause in CNF for the graph coloring problem.

Here is an example presenting how to create a clause:
Let's assume that there is 5 nodes and 3 available colors.
To create a clause X_0_1 OR ~X_1_2 OR X_3_3
you can do:

clause = Clause(5, 3)
clause.add_positive(0, 1)
clause.add_negative(1, 2)
clause.add_positive(3, 3)

The clause must be initialized with the number of nodes and the number of color.
The reason is that we use a 2D index for our variables but the format
imposed by MiniSAT requires a 1D index.
The Clause class automatically handle this change of index, but needs to know the
number of nodes and available colors
"""


class Clause:

    def __init__(self, size: int, colors: int, varname='X'):
        """
        Initialize an empty clause
        :param size: the number of nodes
        :param colors: the number of colors
        :param varname: the name of the variable
        """
        self.varname = varname
        self.n_nodes = size
        self.n_colors = colors
        self.value = []

    def index(self, node_ind: int, color_ind: int) -> int:
        """
        Convert the 2D index of a variable to its corresponding 1D index
        :param node_ind: the node index of the variable
        :param color_ind: the color index of the variable
        :return: the 1D index
        """
        if 0 <= node_ind < self.n_nodes and 0 <= color_ind < self.n_colors:
            return node_ind * self.n_colors + color_ind
        else:
            raise ValueError("Indices : node_ind =", node_ind, "color_ind =", color_ind, "is incorrect")

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
        row_ind, color_ind = divmod(abs(index), self.n_colors)

        if index < 0:
            return '~{0}_{1}_{2}'.format(self.varname, row_ind, color_ind)
        return '{0}_{1}_{2}'.format(self.varname, row_ind, color_ind)

    def add_positive(self, node_ind: int, color_ind: int):
        """
        Add a positive literal to the clause
        :param node_ind: the node index of the variable
        :param color_ind: the color index of the variable
        """
        self.value.append(self.index(node_ind, color_ind)+1)

    def add_negative(self, row_ind, color_ind):
        """
        Add a negative literal to the clause
        :param node_ind: the node index of the variable
        :param color_ind: the color index of the variable
        """
        self.value.append(-self.index(row_ind, color_ind)-1)

    def minisat_str(self):
        return ' '.join([str(x) for x in self.value])

    def __str__(self):
        return ' or '.join([self.str_from_index(x) for x in self.value])
