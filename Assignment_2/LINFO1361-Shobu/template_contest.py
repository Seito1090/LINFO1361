from agent import Agent
import random
import numpy as np

class AI(Agent):
    """An agent that plays following your algorithm.

    This agent extends the base Agent class, providing an implementation your agent.

    Attributes:
        player (int): The player id this agent represents.
        game (ShobuGame): The game the agent is playing.
    """

    num_players = 2

    def print_binary_rep(self, game_state):
        """Prints a numpy board.

        Args:
            game_state (np.ndarray): The board to print. made of bits 2x4, 2 ints16
        """
        white_pawn = '⚪'
        black_pawn = '⚫'
        empty_cell = '⭕'

        print("Board")
        output = [[empty_cell for _ in range(8)] for _ in range(8)]

        for player_id,player in enumerate(game_state):
            for board_id, board_value in enumerate(player):
                row = (board_id == 2 or board_id == 3)*4
                col = (board_id == 1 or board_id == 3)*4
                for cell_id in range(16):
                    if board_value & (1 << 15 - cell_id):
                        output[row + cell_id // 4][col + cell_id % 4] = white_pawn if player_id == 0 else black_pawn

        for id, row in enumerate(output[::-1]):
            if id == 4:
                print()
            print(''.join(row[:4]), ' ', ''.join(row[4: 8]))
            

    def shobuState_to_binary_rep(self, board):
        """Converts a ShobuState to a binarized representation, in a numpy array. (of size play_numx4x2 bytes (8 bytes))

        Args:
            board (list(list(set()))): The board to convert.

        Returns:
            np.ndarray: The converted state.
        """
        # Each quadrant is described by 2 bytes, and the board is 4x4, and there are 2+ players
        game_state = np.zeros((self.num_players, 4), dtype=np.int16)
        for board_id,board_section in enumerate(board):
            for player_id,player in enumerate(board_section):
                for piece in player:
                    game_state[player_id, board_id] |= 1 << 15 - piece
        return game_state
    
    def shobuState_to_bool_array(self, board_shobu):
        """
        Converts a shobu_board to a boolean array
        """
        board_array = np.zeros((self.num_players,4,4,4),dtype=bool)
        for board_id, board_section in enumerate(board_shobu):
            for player_id,player in enumerate(board_section):
                for piece in player:
                    row = 3 - (piece // 4)
                    col = piece % 4
                    board_array[player_id, board_id, row, col] = True
        return board_array

    def bool_array_to_binary_array(self, board_array):
        """
        Converts a boolean array to a binary array, for a shobu board
        """
        board_binary = np.zeros((self.num_players,4),dtype=np.int16)
        for player_id in range(self.num_players):
            for board_id in range(4):
                board_binary[player_id, board_id] = np.packbits(board_array[player_id, board_id]).view(np.int16) 
        return board_binary

    def binary_array_to_bool_array(self, board_binary):
        board_boolean = np.zeros((self.num_players,4,4,4),dtype=bool)
        for player_id in range(self.num_players):
            for board_id in range(4):
                board_boolean[player_id, board_id] = np.unpackbits(np.array([board_binary[player_id,board_id]], dtype=np.uint16).view(np.uint8), bitorder='little').reshape(4,4)
        return board_boolean

    def get_number_of_pawns(self, game_state):
        """Returns the number of pawns for each player.
        
        Args:
            game_state (np.ndarray): The board to convert.

        Returns:
            np.ndarray: The number of pawns for each player, on each board.
        """
        nums = np.zeros((4,self.num_players), dtype=np.int8)
        #np.sum(np.unpackbits(np.array([board_state], dtype=np.uint16).view(np.uint8)))
        for player_id,player in enumerate(game_state):
            for board_id, board_value in enumerate(player):
                nums[board_id, player_id] = np.sum(np.unpackbits(np.array([board_value], dtype=np.uint16).view(np.uint8)))
        return nums
    
    def play(self, state, remaining_time):
        """Determines the next action to take in the given state.

        Args:
            state (ShobuState): The current state of the game.
            remaining_time (float): The remaining time in seconds that the agent has to make a decision.

        Returns:
            ShobuAction: The chosen action.
        """
        binary_rep = self.shobuState_to_binary_rep(state.board)
        self.print_binary_rep(binary_rep)
        print(self.get_number_of_pawns(binary_rep))

        data = (self.bool_array_to_binary_array(self.shobuState_to_bool_array(state.board)))
        print(self.shobuState_to_bool_array(state.board))

        print( self.binary_array_to_bool_array(binary_rep))

        for plate in range(2):
            for board in range(4):
                cell_int16 = binary_rep[plate, board]
                cells = np.unpackbits(np.array([cell_int16], dtype=np.uint16).view(np.uint8), bitorder='little').reshape(4,4)
                print(cells)

        return state.actions[0] # TODO: Replace this with your algorithm.
        ...





    from time import time

    MAX_BORING_ACTIONS = 20
    MAX_DEPTH = 10

    ID_TO_MOVE = 0
    ID_UTILITY = 1
    ID_BOARD = 2
    ID_ACTIONS = 3
    ID_COUNT_BORING_ACTIONS = 4

    # IDEA : Use a tuple to describe a state, so that we can reference it with 'macros' instead of numbers
    # Tuples are faster to create than objects, and are hashable -> Zobrist hashing/Transposition tables

    def play_2(self, state, remaining_time):
        offset_time = self.time() + remaining_time
        player_id = state.to_move
        is_winner = (state.utility == 1) & (player_id == 0) | (state.utility == -1) & (player_id == 1)

        adapted_current_state = (state.to_move, state.utility, state.board, state.actions, state.count_boring_actions)

        # Start the simulation
        return self.simulate(adapted_current_state, player_id, is_winner, offset_time, self.MAX_DEPTH)
    
    def simulate(self, state, player_id, is_winner, offset_time, height):
        # If we are too deep in the simulation, return None
        if height <= 0: return None
        # If the action leads to a stalemate or is boring, stop the simulation
        if state[self.ID_COUNT_BORING_ACTIONS] > self.MAX_BORING_ACTIONS: return None
        # Scoring board for actions
        scores = np.zeros(len(state[self.ID_ACTIONS]))
        # Get all actions possible
        for id, action in enumerate(state[self.ID_ACTIONS]):
            # If the time is up, return the best action
            if self.time() > offset_time: return None
            # Get the next state
            next_state = self.generate_next_state(state, action, self.change_player(player_id))
            # simulate the next state
            next_action = self.simulate(next_state, self.change_player(player_id), is_winner, offset_time, height - 1)
            # Score how good the action is
            scores[id] = self.score_player(state, action, next_state, player_id)
        
        # Return the best action
        return state.actions[np.argmax(scores)] # ?????
        
    def change_player(self, player_id):
        return 1 - player_id
    
    def generate_next_state(self, state, action, player_id): # PRUNING HERE ?
        new_board = state[self.ID_BOARD].copy()
        # Apply the action
        new_board[action[0]] = new_board[action[0]].replace(action[1], '')
        new_board[action[2]] = new_board[action[2]] + action[1]
        # Update the actions
        new_actions = self.game.actions(new_board) # ?????????????????
        # New Utility
        new_utility = self.game.utility(new_board, player_id) # ?????????????????
        # Update the count of boring actions
        count_boring_actions = state[self.ID_COUNT_BORING_ACTIONS] + 1 if len(new_actions) == 1 else 0
        # Return the new state
        return (player_id, new_utility, new_board, new_actions, count_boring_actions)
    
    def score_player(self, state, action, next_state, player_id): # EVAL HERE ?
        min_stones_white = 4
        min_stones_black = 4

        # Just did what the pdf said
        for singleBoard in range(4):
            white_stones, black_stones = next_state[self.ID_BOARD][singleBoard]
            if len(white_stones) < min_stones_white:
                min_stones_white = len(white_stones)
            if len(black_stones) < min_stones_black:
                min_stones_black = len(black_stones)
        
        # To make the relative score on the player id (0 or 1)
        if player_id == 0:
            score = (min_stones_white - min_stones_black) / 1.0
        else:
            score = (min_stones_black - min_stones_white) / 1.0
        
        return score
    
