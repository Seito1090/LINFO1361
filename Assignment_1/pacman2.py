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

def get_PacMan_Position(grid): # Returns the position of the PacMan in the grid
    for i, row in enumerate(grid):
        if 'P' in row:
            return (i, row.index('P'))
    return (-1, -1)

def is_pos(state, pos): #determines if the position is valid or not 
    return 0 <= pos[0] < state.shape[0] and 0 <= pos[1] < state.shape[1] and state.grid[pos[0]][pos[1]] != "#"

def init_new_grid(grid, pos): # Function to initialize a new grid where we can put the PacMan at a new position
    new_grid = [list(row) for row in grid]
    new_grid[pos[0]][pos[1]] = '.'
    return new_grid

def check_integrity(grid): # Function to check the integrity of the grid
    for row in grid:
        if 'P' in row:
            return True
    return False
    
#################
# Problem class #
#################
dico = {}
class Pacman(Problem):
    nbr_fruits = 0

    def __init__(self, initial_state):
        self.initial = initial_state


    def check_direction(self, state, direction, position):
        ''' This function checks what is possible to do in a given direction and returns the result
            The parameters are the state : The current State of the game (State)
                            the direction : The direction in which we want to move (Tuple (int, int))
                         the position : The position of the PacMan in the grid (Tuple (int, int))
        '''

        # First check the position of the PacMan 
        currentPosition = get_PacMan_Position(state.grid)
        if currentPosition == (-1, -1):
            return None 
        
        ''' Then check the direction
            Different directions as follows :
                Up : (-1, 0)
                Down : (1, 0)
                Left : (0, -1)
                Right : (0, 1)
        '''

        # Check if the direction is valid
        new_position = (position[0] + direction[0], position[1] + direction[1])
        while is_pos(state, new_position):
            # If the position is valid, check if there is a fruit to be eaten in that direction
            if state.grid[new_position[0]][new_position[1]] == 'F':
                moves_allowed = (new_position[0] - position[0], new_position[1] - position[1])
                return (moves_allowed, "F")
            
            # Lastly update the position
            new_position = (new_position[0] + direction[0], new_position[1] + direction[1])             

        moves_allowed = (new_position[0] - position[0], new_position[1] - position[1])
        return (moves_allowed, "N")


    def actions(self, state):
        ''' Define the possible actions for a given state (state here represents the grid in which PacMan moves) '''

        # First check the position of the PacMan 
        currentPosition = get_PacMan_Position(state.grid)
        if currentPosition == (-1, -1):
            return None 
        
        # List of possible actions
        possible_actions = [] 

        # Check the possible actions in each direction
        for direction in [(1, 0), (0, -1), (0, 1), (-1, 0)]:
            action = self.check_direction(state, direction, currentPosition)
            if action != None:
                possible_actions.append((action, direction))

        # If a fruit was found, throw it as the first action, 
        possible_actions = sorted(possible_actions, key=lambda x: x[0][1] == "F", reverse=True)
        print("Possible actions: ", possible_actions, "\n Number of fruits: ", self.nbr_fruits)
        
        # Return the list of possible actions

        return possible_actions


    def result(self, state, action):
        ''' This function applies the action to the state and returns a new state
            The parameters are the state : The current State of the game (State)
                            the action : The action to be performed (Tuple (((int, int), string), (int, int)) : (((fursthest_move X, fursthest_move Y), Fruitness), (direction X, direction Y))) 
        '''
        
        # First check the position of the PacMan 
        currentPosition = get_PacMan_Position(state.grid)
        if currentPosition == (-1, -1):
            return None

        # Create a new grid
        new_grid = init_new_grid(state.grid, currentPosition)

        # Check if the action is a fruitfull one 
        if action[0][1] == "F":
            # If the action is fruitfull, we need to update the new grid
            new_position = (currentPosition[0] + action[1][0], currentPosition[1] + action[1][1])
            new_grid[new_position[0]][new_position[1]] = 'P'
            self.nbr_fruits -= 1
        else:
            # If the action is not fruitfull, we need to update the new grid as well
            amount_to_move = action[0][0][0] if action[0][0][0] != 0 else action[0][0][1]
            new_position = (currentPosition[0] + amount_to_move * action[1][0], currentPosition[1] + amount_to_move * action[1][1])
            
            if is_pos(state, new_position):
                new_grid[new_position[0]][new_position[1]] = 'P'
            else:
                new_grid[currentPosition[0]][currentPosition[1]] = 'P'
        
        show_grid(new_grid)
        return State(state.shape, tuple(map(tuple, new_grid)), state.answer, action[1])
        
    def goal_test(self, state): #check for goal state OK
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

    #show_grid(init_state.grid) #HACK : to be removed

    # Example of search
    start_timer = time.perf_counter()
    #node, nb_explored, remaining_nodes = breadth_first_tree_search(problem)
    node, nb_explored, remaining_nodes = breadth_first_graph_search(problem)
    end_timer = time.perf_counter()

    #plot_table(passed_table[0]) #HACK : to be removed

    # Example of print
    path = node.path()

    for n in path:
        # assuming that the __str__ function of state outputs the correct format
        print(n.state)

    print("* Execution time:\t", str(end_timer - start_timer))
    print("* Path cost to goal:\t", node.depth, "moves")
    print("* #Nodes explored:\t", nb_explored)
    print("* Queue size at goal:\t",  remaining_nodes)
