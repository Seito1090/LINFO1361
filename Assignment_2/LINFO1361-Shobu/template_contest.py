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
                    if board_value & (1 << 15-cell_id):
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
                    game_state[player_id, board_id] |= 1 << 15-piece
        return game_state

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

        return state.actions[0] # TODO: Replace this with your algorithm.
        ...
