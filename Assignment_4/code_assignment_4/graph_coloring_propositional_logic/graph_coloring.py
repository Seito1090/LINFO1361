from clause import *

"""
Code generating a list of clauses modeling the graph coloring problem.

It builds clauses using the Clause class defined in clause.py

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


def get_expression():

    # Static definition of the problem
    nodes = {0, 1, 2, 3, 4}
    n_colors = 3
    edges = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),
        (2, 4)
    ]

    expression = []

    # Clauses # 1
    for node in nodes:
        # (x_node_color0 OR x_node_color1 OR x_node_color2 OR .. OR x_node_ncolor)
        clause = Clause(len(nodes), n_colors)
        for color in range(n_colors):
            clause.add_positive(node, color)
        expression.append(clause)

    # Clauses # 2
    for node in nodes:
        for color_a in range(n_colors - 1):
            for color_b in range(color_a + 1, n_colors):
                # (~x_node_color_a OR ~x_node_color_b)
                clause = Clause(len(nodes), n_colors)
                clause.add_negative(node, color_a)
                clause.add_negative(node, color_b)
                expression.append(clause)

    # Clause # 3
    for edge in edges:
        for color in range(n_colors):
            # (~x_edge[0]_color OR ~x_edge[1]_color)
            clause = Clause(len(nodes), n_colors)
            clause.add_negative(edge[0], color)
            clause.add_negative(edge[1], color)
            expression.append(clause)

    return expression
