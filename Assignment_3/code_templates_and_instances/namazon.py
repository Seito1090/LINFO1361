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
                line += 'A' if letter == 'A' else '#'
            board_str += line + "\n"
        return board_str
    def __eq__(self, other):
        return self.pieces == other.pieces
    def __lt__(self, other):
        return self.pieces < other.pieces
    def __hash__(self):
        return hash(str(self.pieces))
    def custom_print(self):
        for i in range(len(self.board)):
            line = ""
            for letter in self.board[i]:
                if letter == 'A':
                    line += '⚪'
                elif letter == '#':
                    line += '⚫'
                elif letter == 'X':
                    line += '🔴'
                else:
                    line += letter
            print(line)

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
        self.initial.board = [[ '#' for i in range(N)] for j in range(N)] 
        pass

    def actions(self, state):
        possible_rows = []
        for row in state.rows:
            # Check if the spot is valid
            if state.board[row][state.current_column] == '#':
                possible_rows.append(row)
        return possible_rows

    def result(self, state, row):
        if state.current_column == self.N+1:
            return state
        new_state = NAmazonsState()
        # Copy the peices
        new_state.pieces = state.pieces.copy(); new_state.pieces.append((row, state.current_column))
        # Copy the rows
        new_state.rows = state.rows.copy(); new_state.rows.remove(row)
        # Copy the board
        new_state.board = [rows.copy() for rows in state.board] # HACK : we could just copy from current_column to the end (reduce memory)
        # Add the new piece
        new_state.board[row][state.current_column] = 'A'
        # Update the current column
        new_state.current_column = state.current_column + 1
        # Remove all the invalid positions
        for cols in range(state.current_column, self.N):
            for rows in new_state.rows:
                # In the rare case that the piece is already placed (to detect bugs)
                if new_state.board[rows][cols] == 'A':
                    new_state.board[rows][cols] = '$'
                # Remove all the diagonals
                if abs(rows - row) == abs(cols - state.current_column):
                    new_state.board[rows][cols] = 'X'
                # Remove the circle
                circle_rad = (rows - row)**2 + (cols - state.current_column)**2
                if circle_rad > 3.5**2 and circle_rad < 4.2**2:
                    new_state.board[rows][cols] = 'X'
        return new_state

    def goal_test(self, state):
        # Goal : if N pieces have been placed
        return len(state.pieces) == self.N

    def h(self, node):
        # Heuristic : Number of spots left (we maximize this value, so we reduce h (to minimize))
        if self.goal_test(node.state):
            return 0
        h = self.N**2
        for row in node.state.rows:
            for piece in node.state.pieces:
                if node.state.board[row][piece[1]] == '#':
                    h -= 1
        return h 

#####################
# Launch the search #
#####################

problem = NAmazonsProblem(int(sys.argv[1]))

start_timer = time.perf_counter()

node = astar_search(problem) # TODO: Launch the search

end_timer = time.perf_counter()

# example of print
path = node.path()

print('Number of moves: ', str(node.depth))

for n in path:

    print(n.state)  # assuming that the _str_ function of state outputs the correct format

    print()
    
print("Time: ", end_timer - start_timer)