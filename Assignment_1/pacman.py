"""
Name of the author(s):
- Charles Lohest <charles.lohest@uclouvain.be>
"""
import time
import sys
from search import *

#Personal functions 
def show_grid(grid): # Function to display the grid
    for row in grid:
        print("".join(row))
    print("\n")

#################
# Problem class #
#################
dico = {}
class Pacman(Problem):

    def actions(self, state):
        possible_actions = []
        # Define the possible actions for a given state (state here represents the grid in which PacMan moves)
        # Detect where the PacMan is in the grid
        position = (0, 0)
        for i, row in enumerate(state.grid):
            if 'P' in row:
                position = (i, row.index('P'))
                break
        # Check for possible moves
        # Up
        if position[0] > 0 and state.grid[position[0] - 1][position[1]] != 'W':
            possible_actions.append('Up')   
        # Down
        if position[0] < state.shape[0] - 1 and state.grid[position[0] + 1][position[1]] != 'W':
            possible_actions.append('Down')
        # Left
        if position[1] > 0 and state.grid[position[0]][position[1] - 1] != 'W':
            possible_actions.append('Left')
        # Right
        if position[1] < state.shape[1] - 1 and state.grid[position[0]][position[1] + 1] != 'W':
            possible_actions.append('Right') 
        # Eat fruit
        print("Possible actions: ", possible_actions)
        show_grid(state.grid)
        pass

    def result(self, state, action):
        # Apply the action to the state and return the new state
        pass
        
    def goal_test(self, state):
    	#check for goal state
        for row in state.grid:
            if 'F' in row:
                return False
        return True



###############
# State class #
###############
class State:

    def __init__(self, shape, grid, answer=None, move="Init"):
        self.shape = shape
        self.answer = answer
        self.grid = grid
        self.move = move

    def __str__(self):
        s = self.move + "\n"
        for line in self.grid:
            s += "".join(line) + "\n"
        return s


def read_instance_file(filepath):
    with open(filepath) as fd:
        lines = fd.read().splitlines()
    shape_x, shape_y = tuple(map(int, lines[0].split()))
    initial_grid = [tuple(row) for row in lines[1:1 + shape_x]]
    initial_fruit_count = sum(row.count('F') for row in initial_grid)

    return (shape_x, shape_y), initial_grid, initial_fruit_count


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: ./Pacman.py <path_to_instance_file>")
    filepath = sys.argv[1]

    shape, initial_grid, initial_fruit_count = read_instance_file(filepath)
    init_state = State(shape, tuple(initial_grid), initial_fruit_count, "Init")
    problem = Pacman(init_state)

    # Example of search
    start_timer = time.perf_counter()
    node, nb_explored, remaining_nodes = breadth_first_tree_search(problem)
    end_timer = time.perf_counter()

    # Example of print
    path = node.path()

    for n in path:
        # assuming that the __str__ function of state outputs the correct format
        print(n.state)

    print("* Execution time:\t", str(end_timer - start_timer))
    print("* Path cost to goal:\t", node.depth, "moves")
    print("* #Nodes explored:\t", nb_explored)
    print("* Queue size at goal:\t",  remaining_nodes)
