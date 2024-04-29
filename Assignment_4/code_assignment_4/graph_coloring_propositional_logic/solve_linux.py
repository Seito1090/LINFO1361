#!/usr/bin/env python3
from graph_coloring import get_expression
import minisat


def get_val_from_index(index: int, n_color: int) -> (int, int):
    """
        Utility function to retrieve the color of the nodes from the set of literal returned as a solution by MiniSAT
        :param index: the index of the literal in the MiniSAT solution
        :param n_color: the number of available colors of the chessboard
        :return: a tuple (node, color)
        """
    index -= 1
    node_ind, color_ind = divmod(abs(index), n_color)
    return node_ind, color_ind


if __name__ == "__main__":

    expression = get_expression()
    nb_vars = 5 * 3 # number of nodes x number of available colors
    solution = minisat.minisat(nb_vars, [clause.minisat_str() for clause in expression], './minisatLinux')

    if solution is None:
        print("The problem is UNSAT")
        exit(0)
    print("The problem is SAT")
    print("Solution : ")
    output = [-1 for i in range(5)]
    for s in solution:
        node, color = get_val_from_index(s, 3)
        output[node] = color

    print(output)