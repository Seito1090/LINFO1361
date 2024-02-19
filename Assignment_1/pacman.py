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

def check_deerper(grid, position, direction):
    # Checks if there is a fruit to be eaten in the direction of the move and how much we can move in that direction
    # Returns the furthest we can go in that direction and the number of fruits in that direction
    # Grid is the grid in which we are moving : 2D array
    # Position is the position of the PacMan in the grid : tuple (x, y)
    # Direction is the direction in which we want to move : string
    # Returns a tuple (int, int) : (furthest, fruits)
    furthest = 0
    fruits = 0
    if direction == "Up":
        while position[0] - furthest > 0 and grid[position[0] - furthest-1][position[1]] != '#':
            if grid[position[0] - furthest][position[1]] == 'F':
                fruits += 1
            furthest += 1
    elif direction == "Down":
        while position[0] + furthest < len(grid)-1 and grid[position[0] + furthest+1][position[1]] != '#':
            if grid[position[0] + furthest][position[1]] == 'F':
                fruits += 1
            furthest += 1
    elif direction == "Left":
        while position[1] - furthest > 0 and grid[position[0]][position[1] - furthest-1] != '#':
            if grid[position[0]][position[1] - furthest] == 'F':
                fruits += 1
            furthest += 1
    elif direction == "Right":
        while position[1] + furthest < len(grid[0])-1 and grid[position[0]][position[1] + furthest+1] != '#':
            if grid[position[0]][position[1] + furthest] == 'F':
                fruits += 1
            furthest += 1
    return (furthest, fruits)

#################
# Problem class #
#################
dico = {}
class Pacman(Problem):

    def actions(self, state):
        possible_actions = []
        action = ""
        # Define the possible actions for a given state (state here represents the grid in which PacMan moves)
        # Detect where the PacMan is in the grid
        position = (0, 0)
        for i, row in enumerate(state.grid):
            if 'P' in row:
                position = (i, row.index('P'))
                break
        # Check for possible moves
        # Up
        if position[0] > 0 and state.grid[position[0] - 1][position[1]] != '#':
            action = check_deerper(state.grid, position, "Up")
            possible_actions.append((action, "Up"))
        # Down
        if position[0] < state.shape[0] - 1 and state.grid[position[0] + 1][position[1]] != '#':
            action = check_deerper(state.grid, position, "Down")
            possible_actions.append((action, "Down"))
        # Left
        if position[1] > 0 and state.grid[position[0]][position[1] - 1] != '#':
            action = check_deerper(state.grid, position, "Left")
            possible_actions.append((action, "Left"))
        # Right
        if position[1] < state.shape[1] - 1 and state.grid[position[0]][position[1] + 1] != '#':
            action = check_deerper(state.grid, position, "Right")
            possible_actions.append((action, "Right"))
        # Eat fruit
        # If there's a fruit to be eaten, it can only be in the possible actions already found
        
        print("Possible actions: ", possible_actions)
        # Return the list of possible actions
        return possible_actions

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
