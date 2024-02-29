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

def arrow_pos(pos:tuple, off:tuple, dist:int):
    #   \x/
    #   xPx
    pos_forw  = (pos[0]          + off[0]*dist, pos[1]          + off[1]*dist) # YX
    pos_latl  = (pos[0] + off[1] + off[0]*dist, pos[1] + off[0] + off[1]*dist) # YX
    pos_latr  = (pos[0] - off[1] + off[0]*dist, pos[1] - off[0] + off[1]*dist) # YX
    pos_diagl = (pos[0] + off[1] + off[0]*dist, pos[1] + off[0] + off[1]*dist) # YX
    pos_diagr = (pos[0] - off[1] + off[0]*dist, pos[1] - off[0] + off[1]*dist) # YX
    return pos_forw, pos_latl, pos_latr, pos_diagl, pos_diagr

def arrow_check(grid:tuple, poses:tuple):
    pos_forw, pos_latl, pos_latr, pos_diagl, pos_diagr = poses # YX
    chk_forw  = is_posG(grid=grid, pos=pos_forw) # YX
    chk_latl  = is_posG(grid=grid, pos=pos_latl) # YX
    chk_latr  = is_posG(grid=grid, pos=pos_latr) # YX
    chk_diagl = is_posG(grid=grid, pos=pos_diagl) # YX
    chk_diagr = is_posG(grid=grid, pos=pos_diagr) # YX
    return chk_forw, chk_latl, chk_latr, chk_diagl, chk_diagr    

def arrow_sprint(grid:tuple, pos: tuple, off:tuple = (0,0)):
    # Compute the offset of the arrow, depending on where the offset is going (up, down, left, right)
    is_bad_choice = False
    side_has_fruit = False
    front_has_fruit = False
    followup_booster = True
    minimal_movement = 1
    furthest = 1
    poses = arrow_pos(pos, off, furthest)
    pos_forw, pos_latl, pos_latr, pos_diagl, pos_diagr = poses # YX
    chk_forw, chk_latl, chk_latr, chk_diagl, chk_diagr = arrow_check(grid, poses)
    
    # While the path is not blocked, we continue to sprint
    while chk_forw:
        furthest += 1
        
        # If the corridor is blocked on both sides, we can continue the sprint
        if not((chk_diagl or chk_diagr) and (chk_latl or chk_latr)):
            minimal_movement += followup_booster
        else:
            followup_booster = False
            # Finds a fruit next to it
            if (chk_latl and  grid[pos_latl[0]][pos_latl[1]] == "F") or (chk_latr and grid[pos_latr[0]][pos_latr[1]] == "F"):
                side_has_fruit = True
                minimal_movement = furthest-1
                break
            # Finds a fruit in front of it
            elif chk_forw :
                if grid[pos_forw[0]][pos_forw[1]] == "F":
                    front_has_fruit = True
                    minimal_movement = furthest-1
                    break

        # Update the positions and checks
        poses = arrow_pos(pos, off, furthest)
        pos_forw, pos_latl, pos_latr, pos_diagl, pos_diagr = poses # YX
        chk_forw, chk_latl, chk_latr, chk_diagl, chk_diagr = arrow_check(grid, poses)
    
    # if the path is blocked, and we are at the end, then don't venture there
    if minimal_movement == furthest and not side_has_fruit and not front_has_fruit:
        is_bad_choice = True

    return is_bad_choice, minimal_movement, furthest, side_has_fruit, front_has_fruit


def actions_dict_arrow(self, state:object, dico:dict):
    curr_pos = get_PacMan_Position(state.grid)
    actions = []
    for offset in [(0,-1), (0,1), (1,0), (-1,0)]: # right, left, up, down
        is_bad, min_travel, fur, rl_f, f_f = arrow_sprint(state.grid, curr_pos, offset)
        new_pos = (curr_pos[0] + offset[0]*min_travel, curr_pos[1] + offset[1]*min_travel)
        if str(new_pos) in state.answer:
            continue
        if not is_bad:
            if f_f:
                actions = [(min_travel, fur, rl_f, f_f, offset, curr_pos, new_pos)]
                break
            elif rl_f:
                actions = [(1, -1, rl_f, f_f, (offset[1], offset[0]), curr_pos, new_pos)]
                break
            else:
                actions.append((min_travel, fur, rl_f, f_f, offset, curr_pos, new_pos))
    return actions

def result_dict_arrow(self, state:object, action:tuple): 
    curr_pos = get_PacMan_Position(state.grid)
    new_grid = [list(row) for row in state.grid]
    new_pos = action[6]
    answer = state.answer.copy()

    answer.setdefault(str(new_pos), 0)
    
    #print(new_pos, curr_pos, action) ; show_grid(state.grid)
    
    if not (new_pos[0] == curr_pos[0] and new_pos[1] == curr_pos[1]):
        new_grid[new_pos[0]][new_pos[1]] = "P"
        new_grid[curr_pos[0]][curr_pos[1]] = "."

     # Return the new state
    new_state = State(state.shape, tuple(map(tuple, new_grid)), answer, f"Move to {new_pos}")
    if self.goal_test(new_state):
        new_state = State(state.shape, tuple(map(tuple, new_grid)), answer, f"Move to {new_pos} Goal")
    return new_state

########################################################################################

#################
# Problem class #
#################
dico = {}
class Pacman(Problem):

    def actions(self, state):
        return actions_dict_arrow(self, state, dico)

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
    init_state = State(shape, tuple(initial_grid), {}, "Init")
    problem = Pacman(init_state)

    #show_grid(init_state.grid) #HACK : to be removed

    # Example of search
    start_timer = time.perf_counter()
    #node, nb_explored, remaining_nodes = breadth_first_tree_search(problem)
    node, nb_explored, remaining_nodes = breadth_first_graph_search(problem)
    #node, nb_explored, remaining_nodes = depth_first_tree_search(problem)
    #node, nb_explored, remaining_nodes = depth_first_graph_search(problem)
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
