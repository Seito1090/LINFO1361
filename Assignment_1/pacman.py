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

def arrow_check(grid:tuple, off_dir:int, dist:int, pos:tuple):
    chk_forw  = is_posG(grid=grid, pos=(pos[0] + off_dir[0]*dist, pos[1] + off_dir[1]*dist)) # YX
    chk_latl  = is_posG(grid=grid, pos=(pos[0] + off_dir[1] + off_dir[0]*dist, pos[1] + off_dir[0] + off_dir[1]*dist)) # YX
    chk_latr  = is_posG(grid=grid, pos=(pos[0] - off_dir[1] + off_dir[0]*dist, pos[1] - off_dir[0] + off_dir[1]*dist)) # YX
    chk_diagl = is_posG(grid=grid, pos=(pos[0] + off_dir[0]*dist + off_dir[1], pos[1] + off_dir[1]*dist + off_dir[0])) # YX
    chk_diagr = is_posG(grid=grid, pos=(pos[0] + off_dir[0]*dist - off_dir[1], pos[1] + off_dir[1]*dist - off_dir[0])) # YX
    return chk_forw, chk_latl, chk_latr, chk_diagl, chk_diagr    

def arrow_sprint(grid:tuple, pos: tuple, off:tuple = (0,0)):
    # Compute the offset of the arrow, depending on where the offset is going (up, down, left, right)
    is_bad_choice = False
    side_has_fruit = False
    front_has_fruit = False
    followup_booster = True
    corridor_len = 0
    furthest = 1
    chk_forw, chk_latl, chk_latr, chk_diagl, chk_diagr = arrow_check(grid, off, furthest, pos)
    
    while chk_forw:
        furthest += 1
        
        if (not is_dl and not is_dr) or (not is_f and not is_r):
            corridor_len += followup_booster
        else:
            followup_booster = False
            if (is_l and  grid[pos_latl[0]][pos_latl[1]] == "F") or (is_r and grid[pos_latr[0]][pos_latr[1]] == "F"):
                side_has_fruit = True
                corridor_len = furthest-1
                break
            elif is_f :
                if grid[pos_forw[0]][pos_forw[1]] == "F":
                    front_has_fruit = True
                    corridor_len = furthest
                    break

        chk_forw, chk_latl, chk_latr, chk_diagl, chk_diagr = arrow_check(grid, off, furthest, pos)
    
    if corridor_len == furthest and not side_has_fruit and not front_has_fruit:
        is_bad_choice = True
    if corridor_len == 0:
        corridor_len = 1
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

    try:
        print(grid[curr_pos[0] - 1][curr_pos[1] - 1], grid[curr_pos[0] - 1][curr_pos[1]], grid[curr_pos[0] - 1][curr_pos[1] + 1])
        print(grid[curr_pos[0]][curr_pos[1] - 1], grid[curr_pos[0]][curr_pos[1]], grid[curr_pos[0]][curr_pos[1] + 1])
        print(grid[curr_pos[0] + 1][curr_pos[1] - 1], grid[curr_pos[0] + 1][curr_pos[1]], grid[curr_pos[0] + 1][curr_pos[1] + 1])
        print("")
    except:
        pass
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
    #node, nb_explored, remaining_nodes = breadth_first_graph_search(problem)
    #node, nb_explored, remaining_nodes = depth_first_tree_search(problem)
    node, nb_explored, remaining_nodes = depth_first_graph_search(problem)
    #node, nb_explored, remaining_nodes = depth_limited_search(problem)
    #node, nb_explored, remaining_nodes = iterative_deepening_search(problem)
    #node, nb_explored, remaining_nodes = uniform_cost_search(problem)
    #node, nb_explored, remaining_nodes = greedy_best_first_graph_search(problem)
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
