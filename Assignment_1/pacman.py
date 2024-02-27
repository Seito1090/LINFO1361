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
    return (furthest, fruits, direction)

def get_PacMan_Position(grid):
    # Returns the position of the PacMan in the grid
    for i, row in enumerate(grid):
        if 'P' in row:
            return (i, row.index('P'))
    return (-1, -1)

class binary_board():
    singleton_created = None
    import numpy as np
    def __init__(self, state):
        if binary_board.singleton_created == None:
            binary_board.singleton_created = self
            self.fruits = np.zeros((state.shape[0], state.shape[1]),dtype=int)
            self.fruits[state.grid == 'F'] = 1
            self.pacman = np.zeros((state.shape[0], state.shape[1]),dtype=int)
            self.pacman[state.grid == 'P'] = 1
            self.walls = np.zeros((state.shape[0], state.shape[1]),dtype=int)
            self.walls[state.grid == '#'] = 1
            self.grid = np.zeros((state.shape[0], state.shape[1]),dtype=int)
            self.grid[state.grid == '.'] = 1
        else:
            return binary_board.singleton_created
    
    def __str__(self):
        table = ""
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                if self.fruits[i,j] == 1:
                    table += "F"
                elif self.pacman[i,j] == 1:
                    table += "P"
                elif self.walls[i,j] == 1:
                    table += "#"
                else:
                    table += "."
            table += "\n"
        return table
    
    def __tuple__(self):
        table = []
        for i in range(self.grid.shape[0]):
            subtable = []
            for j in range(self.grid.shape[1]):
                if self.fruits[i,j] == 1:
                    subtable.append("F")
                elif self.pacman[i,j] == 1:
                    subtable.append("P")
                elif self.walls[i,j] == 1:
                    subtable.append("#")
                else:
                    subtable.append(".")
            table.append(subtable)
        return tuple(table)

    def update(self, position, new_pos):
        self.pacman[position] = 0
        self.pacman[new_pos] = 1
        return tuple(self)

    def explore_direction(self, direction_vec, position):
        type_of_next = "wall"
        try:
            while self.grid[position[0] + direction_vec[0], position[1] + direction_vec[1]] == 1:
                position = (position[0] + direction_vec[0], position[1] + direction_vec[1])
            type_of_next = "fruit" if self.fruits[position[0] + direction_vec[0], position[1] + direction_vec[1]] == 1 else "wall"
        except:
            pass
        return (type_of_next,position)



def is_valid_pos(state, pos):
    return 0 <= pos[0] < state.shape[0] and 0 <= pos[1] < state.shape[1] and state.grid[pos[0]][pos[1]] != "#"

def check_cross(state, pos):
    """Returns the value of each of the 4 movement directions, deppending if there is a wall or a fruit
        Returns : (up, down, left, right)
        Wall = -1
        Fruit = 1
        Empty = 0
    """
    up      = (pos[0], pos[1] + 1) if 0 <= pos[1] + 1 < state.shape[1] else None
    down    = (pos[0], pos[1] - 1) if 0 <= pos[1] - 1 < state.shape[1] else None
    left    = (pos[0] - 1, pos[1]) if 0 <= pos[0] - 1 < state.shape[0] else None
    right   = (pos[0] + 1, pos[1]) if 0 <= pos[0] + 1 < state.shape[0] else None

    check = lambda xy: -1 if xy==None else (state.grid[xy[0]][xy[1]] == "F") * 1 + (state.grid[xy[0]][xy[1]] == "#") * -1

    return (check(up), check(down), check(left), check(right))

def update_pos(grid, pos, new_pos):
    grid[pos[0]][pos[1]] = "."
    grid[new_pos[0]][new_pos[1]] = "P"
    dico[pos] = new_pos # Update the dico with the new position of the PacMan
    return grid

def new_result(self,state, action):
    # Get the position of the PacMan
    position = get_PacMan_Position(state.grid)
    # Generate the new grid
    new_grid = [list(row) for row in state.grid]
    # Select the action to be performed
    action = {"Up": (-1,0), "Down": (1,0), "Left": (0,-1), "Right": (0,1)}[action[2]]
    # Compute the new position
    new_pos = (position[0] + action[0], position[1] + action[1])
    # Update the grid if the new position is valid
    if is_valid_pos(state, new_pos):
        new_grid = update_pos(new_grid, position, new_pos)
    # Return the new state
    return State(state.shape, tuple(map(tuple, new_grid)), state.answer, action[1])

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
        position = get_PacMan_Position(state.grid)
        # Check for possible moves
        # Up
        if position[0] > 0 and state.grid[position[0] - 1][position[1]] != '#':
            possible_actions.append(check_deerper(state.grid, position, "Up"))
        # Down
        if position[0] < state.shape[0] - 1 and state.grid[position[0] + 1][position[1]] != '#':
            possible_actions.append(check_deerper(state.grid, position, "Down"))
        # Left
        if position[1] > 0 and state.grid[position[0]][position[1] - 1] != '#':
            possible_actions.append(check_deerper(state.grid, position, "Left"))
        # Right
        if position[1] < state.shape[1] - 1 and state.grid[position[0]][position[1] + 1] != '#':
            possible_actions.append(check_deerper(state.grid, position, "Right"))
        print("Possible actions: ", possible_actions)
        show_grid(state.grid)
        # Return the list of possible actions

        return possible_actions

    def result(self, state, action):
        # Apply the action to the state and return the new state
        # Action is a peculiar tuple ((int, int), string) : (furthest, fruits), direction
        return new_result(self,state, action)
        # Get the position of the PacMan
        position = get_PacMan_Position(state.grid)

        # Replace the PacMan by a empty space
        new_grid = [list(row) for row in state.grid]
        new_grid[position[0]][position[1]] = '.'
        # Move the PacMan in the direction of the action f
        if action[2] == "Up":
            new_grid[position[0] - 1][position[1]] = 'P'
        elif action[2] == "Down":
            new_grid[position[0] + 1][position[1]] = 'P'
        elif action[2] == "Left":
            new_grid[position[0]][position[1] - 1] = 'P'
        elif action[2] == "Right":
            new_grid[position[0]][position[1] + 1] = 'P'

        return State(state.shape, tuple(map(tuple, new_grid)), state.answer, action[1])
        
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
