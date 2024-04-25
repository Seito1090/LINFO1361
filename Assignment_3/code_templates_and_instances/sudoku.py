import random
import time
import math
import sys



def objective_score(board):
    """ Calculate the score of the board, this is increasing with the number 
    of conflicts on the board. In other words, the lower the better. """
    score = 0
    for row in range(9):
        for col in range(9):
            score += to_add(board, board[row][col], (row, col))
    return score

def to_add(board, value, position):
    ''' This function is used to check if the objective score should be increased or not by returning how much should be added to the score. 
    This is determined based on the conflicts detected '''
    #initial case where we get the initial values in the board, we want to avoid it at all costs 
    if value == 0:
        return 2

    #get the column related to the current position
    col = [board[a][position[1]] for a in range(9)]

    #now remove the value being tested 
    col.remove(value) #only once, if there are duplicates, they will remain ! 

    #check if the value is in the column
    if value in col:
        return 1
    
    #at this point, we know that the value is correct in the rows and in the columns, now we have to check the corresponding square
    #first determine the square 
    square_vals = []
    position_square = [0,0] #offset to put on the rows and columns to get the square
    position_square[0] = 0 if position[0] < 3 else 3 if position[0] < 6 else 6
    position_square[1] = 0 if position[1] < 3 else 3 if position[1] < 6 else 6
    
    for a in range(position_square[0], position_square[0] + 3):
        for b in range(position_square[1], position_square[1] + 3):
            if (a,b) != position:
                square_vals.append(board[a][b])

    if value in square_vals:
        return 1
    
    return 0

def generate_possible_values(board, initial_positions):
    """ Generate a list of possible values for a row. """
    possible_values = [[x for x in range(1, 10)] for _ in range(9)]
    for a,b in initial_positions:
        possible_values[a].remove(board[a][b])
    return possible_values

def generate_neighbor(board, init_positions, possible_values, option):
    """ Generate a neighbor of the board by swapping the values of random cells, excluding the initial positions. """
    admisible = [1,2,3,4,5,6,7,8,9]
    neighbor = [row[:] for row in board]

    #Copy the initial values 
    for i,j in init_positions:
        neighbor[i][j] = board[i][j]
    
    for row in range(9):
        choices = possible_values[row]
        for col in range(9):
            if (row,col) not in init_positions:
                choice = random.choice(choices)
                choices.remove(choice)
                neighbor[row][col] = choice

    return neighbor


def simulated_annealing_solver(initial_board):
    """Simulated annealing Sudoku solver."""

    init_positions = [(i,j) for i in range(9) for j in range(9) if initial_board[i][j] != 0]

    current_solution = [row[:] for row in initial_board]
    best_solution = current_solution
    
    current_score = objective_score(current_solution)
    best_score = current_score

    temperature = 1.0
    cooling_rate = 0.99999 #TODO: Adjust this parameter to control the cooling rate

    while temperature > 0.0001:

        try:  
            possible_values = generate_possible_values(current_solution, init_positions)
            #print(f"possible values are {possible_values}")
            # TODO: Generate a neighbor (Don't forget to skip non-zeros tiles in the initial board ! It will be verified on Inginious.)
            neighbor = generate_neighbor(current_solution, init_positions, possible_values, temperature)
           

            # Evaluate the neighbor
            neighbor_score = objective_score(neighbor)

            # Calculate acceptance probability
            delta = float(current_score - neighbor_score)

            if current_score == 0:

                return current_solution, current_score

            # Accept the neighbor with a probability based on the acceptance probability
            
            if neighbor_score < current_score or (neighbor_score > 0 and math.exp((delta/temperature)) > random.random()):

                current_solution = neighbor
                current_score = neighbor_score

                if (current_score < best_score):
                    best_solution = current_solution
                    best_score = current_score

            # Cool down the temperature
            temperature *= cooling_rate
            
        except:

            print("Break asked")
            break
        
    return best_solution, best_score

 
def print_board(board):

    """Print the Sudoku board."""

    for row in board:
        print("".join(map(str, row)))

 

def read_sudoku_from_file(file_path):
    """Read Sudoku puzzle from a text file."""
    
    with open(file_path, 'r') as file:
        sudoku = [[int(num) for num in line.strip()] for line in file]

    return sudoku
 

if __name__ == "__main__":

    # Reading Sudoku from file
    initial_board = read_sudoku_from_file(sys.argv[1])

    # Solving Sudoku using simulated annealing
    start_timer = time.perf_counter()

    solved_board, current_score = simulated_annealing_solver(initial_board)

    end_timer = time.perf_counter()

    print_board(solved_board)
    print("\nValue(C):", current_score)

    # print("\nTime taken:", end_timer - start_timer, "seconds")