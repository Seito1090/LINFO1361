from search import *
import time

#################
# Problem class #
#################

class NAmazonsState:
    depth = 0
    current_column = 0
    rows = []
    pieces = []
    board = []
    def __str__(self):
        board_str = ""
        for i in range(len(self.board)):
            line = ""
            for letter in self.board[i]:
                line += 'A' if letter == 'A' else letter
            board_str += line + "\n"
        return board_str
    def __eq__(self, other):
        return self.pieces == other.pieces
    def __lt__(self, other):
        return self.pieces < other.pieces
    def __hash__(self):
        return hash(str(self.pieces))
            

class NAmazonsProblem(Problem):
    """The problem of placing N amazons on an NxN board with none attacking
    each other. A state is represented as an N-element array, where
    a value of r in the c-th entry means there is an empress at column c,
    row r, and a value of -1 means that the c-th column has not been
    filled in yet. We fill in columns left to right.
    """
    def __init__(self, N):
        self.N = N
        self.initial = NAmazonsState()
        self.initial.current_column = 0
        self.initial.rows = [i for i in range(N)]
        self.initial.board = [['#' for i in range(N)] for j in range(N)]
        pass

    def actions(self, state):
        if state.current_column == self.N-1:
            return []
        else:
            possible_rows = []
            for row in state.rows:
                if state.board[row][state.current_column+1] == '#':
                    possible_rows.append(row)
            return possible_rows

    def result(self, state, row):
        if state.current_column == self.N-1:
            return state
        new_state = NAmazonsState()
        new_state.pieces = state.pieces.copy()
        new_state.pieces.append((row, state.current_column))
        new_state.current_column = state.current_column + 1
        new_state.rows = state.rows.copy()
        new_state.rows.remove(row)
        new_state.board = [rows.copy() for rows in state.board]
        new_state.board[row][state.current_column] = 'A'
        for cols in range(state.current_column, self.N):
            for rows in new_state.rows:
                if new_state.board[rows][cols] == 'A':
                    continue
                # Remove all the diagonals
                if abs(rows - row - cols) < 1:
                    new_state.board[rows][cols] = 'X'
                if abs(rows - row + cols) < 1:
                    new_state.board[rows][cols] = 'X'
                # Remove the circle
                circle_rad = (rows - row)**2 + (cols - state.current_column)**2
                if circle_rad > 10 and circle_rad < 18:
                    new_state.board[rows][cols] = 'X'
        return new_state

    def goal_test(self, state):
        return len(state.rows) == 0 or len(state.pieces) == self.N or state.current_column == self.N-1

    def h(self, node):
        h = node.state.current_column
        for row_data in node.state.board:
            if '#' == row_data[node.state.current_column]:
                h += 1
        return h    

#####################
# Launch the search #
#####################

problem = NAmazonsProblem(int(sys.argv[1]))

start_timer = time.perf_counter()

node = astar_search(problem) # TODO: Launch the search

end_timer = time.perf_counter()

print(node)
exit()

# example of print
path = node.path()

print('Number of moves: ', str(node.depth))

for n in path:

    print(n.state)  # assuming that the _str_ function of state outputs the correct format

    print()
    
print("Time: ", end_timer - start_timer)