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

def get_PacMan_Position(grid):
    # Returns the position of the PacMan in the grid
    for i, row in enumerate(grid):
        if 'P' in row:
            return (i, row.index('P'))
    return (-1, -1)

def is_posG(grid:tuple, pos:tuple):
    if 0 <= pos[0] < len(grid) and 0 <= pos[1] < len(grid[0]):
        return grid[pos[0]][pos[1]] != "#"
    return  False

def is_pos(state:object, pos:tuple):
    return 0 <= pos[0] < state.shape[0] and 0 <= pos[1] < state.shape[1] and state.grid[pos[0]][pos[1]] != "#"

##############################################################################

def arrow_sprint(grid:tuple, pos: tuple, off:tuple = (0,0)):
    # Compute the offset of the arrow, depending on where the offset is going (up, down, left, right)
    pos_forw = (pos[0] + off[0], pos[1] + off[1])
    pos_latl = (pos[0] + off[1], pos[1] + off[0])
    pos_latr = (pos[0] - off[1], pos[1] - off[0])
    pos_diagl = (pos[0] + off[0] + off[1], pos[1] + off[1] + off[0])
    pos_diagr = (pos[0] + off[0] - off[1], pos[1] + off[1] - off[0])
    is_bad_choice = False
    side_has_fruit = False
    front_has_fruit = False
    continue_corridor = True
    furthest = 0
    corridor_len = 0
    
    while is_posG(grid=grid, pos=pos_forw):
        furthest += 1
        is_f = is_posG(grid=grid, pos=pos_forw)
        is_l = is_posG(grid=grid, pos=pos_latl)
        is_r = is_posG(grid=grid, pos=pos_latr)
        is_dl = is_posG(grid=grid, pos=pos_diagl)
        is_dr = is_posG(grid=grid, pos=pos_diagr)
        
        if ((not is_dl and not is_dr) or (not is_f and not is_r)) and continue_corridor:
            corridor_len += 1
        else:
            continue_corridor = False
            if (is_l and  grid[pos_latl[0]][pos_latl[1]] == "F") or (is_r and grid[pos_latr[0]][pos_latr[1]] == "F"):
                side_has_fruit = True
                corridor_len = furthest-1
                break
            elif is_f :
                if grid[pos_forw[0]][pos_forw[1]] == "F":
                    front_has_fruit = True
                    corridor_len = furthest
                    break

        pos_forw = (pos_forw[0] + off[0], pos_forw[1] + off[1])
        pos_latl = (pos_latl[0] + off[0], pos_latl[1] + off[1])
        pos_latr = (pos_latr[0] + off[0], pos_latr[1] + off[1])
        pos_diagl = (pos_diagl[0] + off[0], pos_diagl[1] + off[1])
        pos_diagr = (pos_diagr[0] + off[0], pos_diagr[1] + off[1])
    
    if corridor_len == furthest and not side_has_fruit and not front_has_fruit:
        is_bad_choice = True
    if corridor_len == 0:
        corridor_len = 1 #+ is_posG(grid=grid, pos=(pos_forw[0] + off[0], pos_forw[1] + off[1]))
    return is_bad_choice, corridor_len, furthest, side_has_fruit, front_has_fruit

def dico_register(dico:dict, key:tuple):
    if key not in dico:
        dico[key] = 1
    else:
        dico[key] += 1

def dico_register_fruit(dico:dict, pos_fruit:tuple):
    if 'fruits' not in dico:
        dico['fruits'] = [pos_fruit]
    else:
        dico['fruits'].append(pos_fruit)

def actions_dict_arrow(self, grid:tuple, dico:dict):
    curr_pos = get_PacMan_Position(grid)
    actions = []
    for offset in [(0,1), (0,-1), (1,0), (-1,0)]: # bottom, right, left, top
        is_bad, corr_len, fur, rl_f, f_f = arrow_sprint(grid, curr_pos, offset)
        if not is_bad and (curr_pos[0] + offset[0]*corr_len, curr_pos[1] + offset[1]*corr_len) not in dico:
            if f_f:
                actions = [(corr_len, fur, rl_f, f_f, offset)]
                dico_register_fruit(dico, (curr_pos[0] + offset[0]*corr_len, curr_pos[1] + offset[1]*corr_len))
                break
            elif rl_f:
                actions = [(1, -1, rl_f, f_f, (-offset[1], offset[0]))]
                break
            else:
                dico_register(dico, (curr_pos[0] + offset[0]*corr_len, curr_pos[1] + offset[1]*corr_len))
                actions.append((corr_len, fur, rl_f, f_f, offset))
    return actions

def result_dict_arrow(self, state:object, action:tuple): 
    curr_pos = get_PacMan_Position(state.grid)
    new_grid = [list(row) for row in state.grid]
    new_pos = (curr_pos[0] + action[4][0]*action[0], curr_pos[1] + action[4][1]*action[0])
    
    #print(new_pos, curr_pos, action) ; show_grid(state.grid)
    
    if not (new_pos[0] == curr_pos[0] and new_pos[1] == curr_pos[1]):
        new_grid[new_pos[0]][new_pos[1]] = "P"
        new_grid[curr_pos[0]][curr_pos[1]] = "."

     # Return the new state
    new_state = State(state.shape, tuple(map(tuple, new_grid)), state.answer, f"Move to {new_pos}")
    if self.goal_test(new_state):
        new_state = State(state.shape, tuple(map(tuple, new_grid)), state.answer, f"Move to {new_pos} Goal")
    return new_state

def dico_to_graph(dico:dict):
    import matplotlib.pyplot as plt
    table = [[0 for i in range(10)] for j in range(10)]
    for key in dico:
        if key != 'fruits':
            new_key = tuple(key)
            table[new_key[0]][new_key[1]] = dico[key]
    plt.imshow(table, cmap='hot', interpolation='nearest')
    plt.colorbar()
    plt.show()

########################################################################################

#################
# Problem class #
#################
dico = {}
class Pacman(Problem):

    def actions(self, state):
        return actions_dict_arrow(self, state.grid, dico)

    def result(self, state, action):
        # Apply the action to the state and return the new state
        return result_dict_arrow(self,state, action)
        
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

def check_grids(path):
    positions = [0] #List of indexes of the states to keep
    #This function will itterate through the path, check all the states and see if the pacman could have jumped over a few positions instead of what he did
    for a in range(len(path) - 1):
        current_grid = path[a].state.grid
        current_point = get_PacMan_Position(current_grid)
        next_grid = path[a + 1].state.grid
        next_point = get_PacMan_Position(next_grid)
        
        # Check if the PacMan moved to a fruit
        if current_grid[next_point[0]][next_point[1]] == "F":
            positions.append(a+1)
        else:
            # Check if there's a change in line
            if a != 0:
                previous_grid = path[a - 1].state.grid
                previous_point = get_PacMan_Position(previous_grid)
                current_direction = (current_point[0] - previous_point[0], current_point[1] - previous_point[1])
                next_direction = (next_point[0] - current_point[0], next_point[1] - current_point[1])
                if current_direction != next_direction:
                    if (current_grid[current_point[0]][current_point[1]] != "F"):
                        positions.append(a)

    new_path = [path[i] for i in positions]
    return new_path
    
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
    path = check_grids(path)
    node.depth = len(path)-1

    check_grids(path)

    for n in path:
        # assuming that the __str__ function of state outputs the correct format
        print(n.state)

    print("* Execution time:\t", str(end_timer - start_timer))
    print("* Path cost to goal:\t", node.depth, "moves")
    print("* #Nodes explored:\t", nb_explored)
    print("* Queue size at goal:\t",  remaining_nodes)
