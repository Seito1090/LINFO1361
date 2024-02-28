
class binary_board():
    singleton_created = None
    
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


def virtual_explore(state, pos:tuple, dir:tuple):
    """
    Function to look in a cross shape in a direction, if there are walls, when do they stop, if there are fruits, 
    how many and how far you can go
    If there is a fruit within the path, then the function returns the direction of the fruit and the distance to it
    """
    enclosement_distance = 0
    enclosement_continue = True

    fruit_count = 0
    fruit_dir = None
    fruit_distance = -1

    max_distance = 0
    if is_pos(state, (pos[0] + dir[0], pos[1] + dir[1])):
        while state.grid[pos[0] + dir[0], pos[1] + dir[1]] == 1:
            #update the position
            pos = (pos[0] + dir[0], pos[1] + dir[1])
            #update the max distance
            max_distance += 1
            #check if the next position is a wall or a fruit or the edge of the map
            cross_test = check_cross(state, pos)
            #if the next position is a wall, then we check if the enclosement is still going on (BUG: if 2 walls in zigzag, then it will not work properly)
            if enclosement_continue:
                enclosement_distance += any(cross_test == -1)
            else:
                enclosement_continue = False
            #if the next position is a fruit, then we update the fruit count and the direction and distance to the fruit
            if any(cross_test==1):
                fruit_count += 1
                #if the fruit is the first one, then we update the direction and the distance
                if fruit_dir == None:
                    fruit_dir = dir
                    fruit_distance = max_distance
            #if the next position is a wall, then we stop the loop
            if not is_pos(state, (pos[0] + dir[0], pos[1] + dir[1])):
                break
    return (enclosement_distance,max_distance, fruit_count, fruit_dir, fruit_distance)
        


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

def new_old_result(self,state, action):
    # Get the position of the PacMan
    position = get_PacMan_Position(state.grid)
    # Generate the new grid
    new_grid = [list(row) for row in state.grid]
    # Select the action to be performed
    action_do = {"Up": (-1,0), "Down": (1,0), "Left": (0,-1), "Right": (0,1)}[action[2]]
    # Compute the new position
    new_pos = (position[0] + action_do[0], position[1] + action_do[1])
    # Update the grid if the new position is valid
    if is_pos(state, new_pos):
        new_grid = update_pos(new_grid, position, new_pos)
    # Return the new state
    return State(state.shape, tuple(map(tuple, new_grid)), state.answer, action[2])


def arrow_explore(state, pos:tuple, dir:tuple):
    # vertical | horizontal
    off_3 = (pos[0], pos[1] + dir[1] + 1) if dir[1] != 0 else (pos[0] + dir[0] + 1, pos[1]) # point

    distance_max = 0
    distance_close = 0
    fruit_offset = None
    while is_pos(state, off_3):
        off_1 = (pos[0] - 1, pos[1] + dir[1]) if dir[1] != 0 else (pos[0] + dir[0], pos[1] + 1) # left
        off_2 = (pos[0] + 1, pos[1] + dir[1]) if dir[1] != 0 else (pos[0] - dir[0], pos[1] - 1) # right
        off_3 = (pos[0], pos[1] + dir[1] + 1) if dir[1] != 0 else (pos[0] + dir[0] + 1, pos[1]) # point
        for xy in [off_1, off_2, off_3]:
            if is_pos(state, xy): # TODO: BUG ?
                if state.grid[xy[0]][xy[1]] == "F":
                    fruit_offset = xy
        distance_close += 1  # TODO: check if the distance is correct
        distance_max += 1 # TODO : add checks
        dir = (dir[0] + (dir[0]!=0), dir[1] + (dir[1]!=0))
    
    return (distance_close, distance_max, fruit_offset)

#....##....
#.#........
#.##...#.#..
#.#...##F#.
#...P..###.
#.#........
#.####...#.
#..........

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

########################################################################################

passed_table =[None]


def print_table(table):
    for row in table:
        print(''.join(f"{element:3}" for element in row))
    print("\n")

def init_table(state):
    table = [[0 for _ in range(state.shape[1]+1)] for _ in range(state.shape[0]+1)]
    for i in range(state.shape[0]+1):
        for j in range(state.shape[1]+1):
            if not is_pos(state, (i,j)):
                table[i][j] = -1
            elif state.grid[i][j] == "F":
                table[i][j] = 1
    return table

def new_action_table(self, state, passed_table):
    # Get the position of the PacMan
    curr_pos = get_PacMan_Position(state.grid)
    # Generate the trace table
    if passed_table[0] == None:
        passed_table[0] = init_table(state)
        passed_table[0][curr_pos[0]][curr_pos[1]] = -2
    # Check the possible actions
    actions = []
    curr_value = passed_table[0][curr_pos[0]][curr_pos[1]]
    for i in range(4):
        if passed_table[0][curr_pos[0] + [0,0,-1,1][i]][curr_pos[1] + [1,-1,0,0][i]] >= 0:
            actions.append((curr_pos[0] + [0,0,-1,1][i], curr_pos[1] + [1,-1,0,0][i]))
            val = passed_table[0][curr_pos[0] + [0,0,-1,1][i]][curr_pos[1] + [1,-1,0,0][i]] # You will explore this at some point
            passed_table[0][curr_pos[0] + [0,0,-1,1][i]][curr_pos[1] + [1,-1,0,0][i]] = curr_value-1 if val == 0 else 1
    #print_table(passed_table[0])
    return actions

def new_result_table(self, state, action):
    #Apply the action to the state and return the new state
    # Get the position of the PacMan
    curr_pos = get_PacMan_Position(state.grid)
    # Generate the new grid
    new_grid = [list(row) for row in state.grid]
    # Update the grid if the new position is valid
    if is_pos(state, action):
        new_grid[action[0]][action[1]] = "P"
        new_grid[curr_pos[0]][curr_pos[1]] = "."
    # Return the new state
    new_state = State(state.shape, tuple(map(tuple, new_grid)), state.answer, f"Move to {action}")
    if self.goal_test(new_state):
        new_state = State(state.shape, tuple(map(tuple, new_grid)), state.answer, f"Move to {action} Goal")
    return new_state

def plot_table(table):
    import matplotlib.pyplot as plt
    plt.imshow(table, cmap='hot', interpolation='nearest')
    plt.colorbar()
    plt.show()