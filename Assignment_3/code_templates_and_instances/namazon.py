from search import *
import time

#################
# Problem class #
#################

class NAmazonsProblem(Problem):
    """The problem of placing N amazons on an NxN board with none attacking
    each other. A state is represented as an N-element array, where
    a value of r in the c-th entry means there is an empress at column c,
    row r, and a value of -1 means that the c-th column has not been
    filled in yet. We fill in columns left to right.
    """
    def __init__(self, N):
        pass

    def actions(self, state):
        pass

    def result(self, state, row):
        pass

    def goal_test(self, state):
        pass

    def h(self, node):
        h = 0.0

        return h    

#####################
# Launch the search #
#####################

problem = NAmazonsProblem(int(sys.argv[1]))

start_timer = time.perf_counter()

node = ... # TODO: Launch the search

end_timer = time.perf_counter()


# example of print
path = node.path()

print('Number of moves: ', str(node.depth))

for n in path:

    print(n.state)  # assuming that the _str_ function of state outputs the correct format

    print()
    
print("Time: ", end_timer - start_timer)