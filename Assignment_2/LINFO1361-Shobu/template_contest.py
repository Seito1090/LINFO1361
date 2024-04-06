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

    # ---------------------------------------------- #
    # ------------- Shobu Agent Logic -------------- #
    
    directions = np.array([(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)])
    num_players = 2
    max_depth = 2
    masks_tuple = None
    binary_transposition_table = None

    def __init__(self):
        self.max_depth = 2
        self.binary_transposition_table = dict()
        self.binary_mask_init_generation()

    def play(self, state, remaining_time):
        """Determines the next action to take in the given state.

        Args:
            state (ShobuState): The current state of the game.
            remaining_time (float): The remaining time in seconds that the agent has to make a decision.

        Returns:
            ShobuAction: The chosen action.
        """
        # Convert the board to a binary board
        binary_board = self.binary_board_from_shobu_board(state.board)

        # Translate the actions, and don't sort them (so we can select them from the original list)
        'binary_action_masks = self.binary_mask_actions(binary_board, state.to_move)'
        binary_actions = self.binary_action_from_shobu_action(binary_board, state.to_move, state.actions)
        binary_state = self.binary_state_wrapper(binary_board, state.to_move, state.utility, binary_actions)

        # Simulations to find the best action
        best_action_idx = self.binary_aplha_beta_search(binary_state, remaining_time)
        
        if best_action_idx is None:
            return None
        return state.actions[best_action_idx]

    # ---------------------------------------------- #
    # -------------- Shobu to Binary --------------- #
    def binary_board_from_shobu_board(self, shobu_board):
        """ Converts a shobu board to a binary board
        
        Args:
            shobu_board (list(list(set()))): The board to convert.
            
        Returns:
            np.ndarray[2,4,uint16]: The converted state.
        """
        binary_board = np.zeros((2, 4), dtype=np.uint16)
        for board_quadrant_id, board_quadrant in enumerate(shobu_board):
            for player_id, player in enumerate(board_quadrant):
                for piece in player:
                    binary_board[player_id, board_quadrant_id] |= 1 <<piece
        return binary_board

    def binary_action_from_shobu_action(self, binary_board:np.ndarray, player_id:int, shobu_action:tuple):
        """Converts a shobu action to a binary action
        
        Args:
            binary_board (np.ndarray[2,4,uint16]): The binary board
            player_id (int): The player id
            shobu_action (tuple): The action to convert.
            
        Returns:
            list(tuple[10](uint16(mask_o), uint16(mask), uint16(mask_r), uint16(mask_p), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone)): The converted action.
        """
        actions = []
        # For every action
        for action in shobu_action:
            passive_board, passive_stone, active_board, active_stone, direction, length = action
            # Compute the different masks
            mask_o = 1 << passive_stone
            mask = 0
            for i in range(1, length+1):
                mask |= 1 << (passive_stone + i*direction)
            mask_r = 1 << (passive_stone + length*direction)
            # Add a pushing action if needed (no other check since its already been done in the shobu action generation)
            if np.any(mask & binary_board[self.next_player(player_id), active_board]):
                mask_p = 1 << (passive_stone + (length+1)*direction)
            else:
                mask_p = 0
            # Add the action
            actions.append((mask_o, mask, mask_r, mask_p, direction, length, passive_board, passive_stone, active_board, active_stone))
        return actions

    def print_binary_board(self, binary_board:np.ndarray):
        """Prints the binary board

        Args:
            binary_board (np.ndarray[2,4,uint16]): The binary board        
        """
        quadrants_player_0 = np.unpackbits(binary_board[0], axis=1)
        quadrants_player_1 = np.unpackbits(binary_board[1], axis=1)
        
        output_string = ["" for _ in range(9)]
        for line_id in range(8):
            true_line_id = line_id + line_id // 4
            for quadrant_id in [2,3] if line_id >= 4 else [0,1]:
                output_string[true_line_id] += " ".join([str(int(quadrants_player_0[quadrant_id, line_id])) for _ in range(4)])
                output_string[true_line_id] += " "
                output_string[true_line_id] += " ".join([str(int(quadrants_player_1[quadrant_id, line_id])*2) for _ in range(4)])
        
        for line in output_string:
            print(line)           

    # ----------------------------------------------- #
    # ----------------- Binary Masks ---------------- #

    def binary_mask_init_generation(self):
        """Generates all masks needed for the binary representation of the board
        Must only be called once, and the masks must be stored in a variable
        
        Returns:
            tuple(np.ndarray[4,4,8], np.ndarray[4,4,8,4], np.ndarray[4,4,8,4], np.ndarray[4,4,8,4]): (mask_origins, masks, mask_results, mask_push_result)
        """
        masks = np.zeros((4,4,8,4), dtype=np.uint16) # Mask of the move to clear it all, and check where you arrive (has the resulting position, but not the origin)
        mask_results = np.zeros((4,4,8,4), dtype=np.uint16) # Mask for only the resulting position of the stone
        mask_origins = np.zeros((4,4,8), dtype=np.uint16) # Mask for only the original position of the stone
        mask_push_result = np.zeros((4,4,8,4), dtype=np.uint16) # Mask for only the pushed stone
        for x in range(4):
            for y in range(4):
                for direction_id, direction in enumerate(self.directions):
                    origin = 1 << (4*x + y)
                    for length in range(1, 4): # Length 0 is the origin, so we start at 1
                        new_x = x + length*direction[0]
                        new_y = y + length*direction[1]
                        if new_x < 0 or new_x >= 4 or new_y < 0 or new_y >= 4:
                            break
                        masks[x,y,direction_id,length] = 1 << (4*new_x + new_y)
                        mask_results[x,y,direction_id,length] = 1 << (4*x + y)
                        if length < 3 and new_x >= 1 and new_x < 3 and new_y >= 1 and new_y < 3:
                            mask_push_result[x,y,direction_id,length] = 1 << (4*(new_x + direction[0]) + new_y + direction[1])
                    # Mark the origin
                    mask_origins[x,y,direction_id] = origin

        self.masks_tuple = (mask_origins, masks, mask_results, mask_push_result)
    
    def binary_mask_filter(self, binary_board:np.ndarray, player_id:int, passive_board:int, passive_stone:int, active_board:int, active_stone:int):
        """Filters the masks to get only the valid ones for a move
        
        Args:
            mask_tuple (tuple(np.ndarray[4,4,8], np.ndarray[4,4,8,4], np.ndarray[4,4,8,4]): The tuple of masks
            binary_board (np.ndarray[2,4,uint16]): The binary board
            player_id (int): The player id
            passive_board (int): The passive board
            passive_stone (int): The passive stone
            active_board (int): The active board
            active_stone (int): The active stone

        Returns:
            list(tuple[10](uint16(mask_o), uint16(mask), uint16(mask_r), uint16(mask_p), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone)): The filtered masks (mask_o, mask, mask_r, direction, length, passive_board, passive_stone, active_board, active_stone
        """
        x_passive = passive_stone // 4
        y_passive = passive_stone % 4
        x_active = active_stone // 4
        y_active = active_stone % 4
        if passive_stone >= 16 or active_stone >= 16: # 4x4 board
            return []
        if passive_board >= 4 or active_board >= 4: # 2x2 boards
            return []
        if passive_board % 2 == active_board % 2: # The boards must be on different sides
            return []
        if player_id == 0 and passive_board >= 2: # White player's passive board is on black player's side
            return []
        elif player_id == 1 and passive_board < 2: # Black player's passive board is on white player's side
            return []
        masked_results = []
        ennemy_player_id = self.next_player(player_id)
        mask_origins, masks, mask_results, mask_push_result = self.masks_tuple
        # Check if the passive stone will not push a ennemy stone
        for direction_id in range(8):
            for length_id in range(4):
                # Check if the path is clear as a passive stone
                if binary_board[ennemy_player_id, passive_board] & masks[x_passive, y_passive, direction_id, length_id]:
                    continue
                # Check that the stone can attack (not more than 1 stone), and that if you push a stone, it is valid
                if np.sum(np.unpackbits((binary_board[player_id, active_board] & masks[x_active, y_active, direction_id, length_id]) 
                        | (mask_push_result[x_active, y_active, direction_id, length_id] & binary_board[ennemy_player_id, active_board])
                        | (mask_push_result[x_active, y_active, direction_id, length_id] & binary_board[player_id, active_board]), axis=1)) > 1:
                    continue
                ellement = (mask_origins[x_passive, y_passive, direction_id],
                            masks[x_passive, y_passive, direction_id, length_id], 
                            mask_results[x_passive, y_passive, direction_id, length_id],
                            mask_push_result[x_passive, y_passive, direction_id, length_id],
                            direction_id,
                            length_id,
                            passive_board,
                            passive_stone,
                            active_board,
                            active_stone)
                masked_results.append(ellement) # TODO : Check if pushing a stone is valid
        return masked_results

    def binary_mask_sort(self, binary_board:np.ndarray, player_id:int, actions:list):
        """Sorts the actions based on a heuristic
        
        Args:
            binary_board (np.ndarray[2,4,uint16]): The binary board
            player_id (int): The player id
            actions (list(tuple[10](uint16(mask_o), uint16(mask), uint16(mask_r), uint16(mask_p), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone))): The actions to sort

        Returns:
            list(tuple[10](uint16(mask_o), uint16(mask), uint16(mask_r), uint16(mask_p), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone)): The sorted masks
        """
        return sorted(actions, key=lambda x: self.binary_heuristic_evaluation(self.binary_apply_action(binary_board, player_id, x), player_id), reverse=True)

    def binary_heuristic_evaluation(self, binary_board:np.ndarray, player_id:int):
        """Heuristic evaluation of the binary board
        
        Args:
            binary_board (np.ndarray[2,4,uint16]): The binary board
            player_id (int): The player id

        Returns:
            int: The heuristic evaluation
        """
        return np.sum([self.binary_heuristic_quadrant(binary_board, player_id, quadrant_id) for quadrant_id in range(4)])

    def binary_heuristic_quadrant(self, binary_board:np.ndarray, player_id:int, quadrant_id:int):
        """Heuristic evaluation of a quadrant of the board.

        Objective :
            - Defend as much as possible
            - Attack as much as possible
            - If the enemy is close, attack
        """
        number_of_pawns = np.sum(np.unpackbits(binary_board[player_id, quadrant_id], axis=1))
        number_of_enemy_pawns = np.sum(np.unpackbits(binary_board[self.next_player(player_id), quadrant_id], axis=1))
        smallest_distance = 4
        for player_pawn in np.where(np.unpackbits(binary_board[player_id, quadrant_id], axis=1))[0]:
            for enemy_pawn in np.where(np.unpackbits(binary_board[self.next_player(player_id), quadrant_id], axis=1))[0]:
                distance = abs(player_pawn - enemy_pawn)
                if distance < smallest_distance:
                    smallest_distance = distance
        # ---------------------------------------------------------
        score = (5-number_of_pawns)**2 # Defend as much as possible
        score += (5 - number_of_enemy_pawns) # Attack as much as possible
        score += (4-smallest_distance) # if the enemy is close, attack
        return score
    
    def binary_mask_actions(self, binary_board:np.ndarray, player_id:int):
        """Geeenrates all the possible actions for a player
        
        Args:
            binary_board (np.ndarray[2,4,uint16]): The binary board
            player_id (int): The player id

        Returns:
            list(tuple[10](uint16(mask_o), uint16(mask), uint16(mask_r), uint16(mask_p), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone)): The filtered masks
        """
        all_mask_actions = []
        for passive_board in [0,1] if player_id == 0 else [2,3]:
            for active_board in [1,3] if passive_board in [0,2] else [0,2]:
                for passive_stone in np.where(np.unpackbits(binary_board[player_id, passive_board], axis=1))[0]:
                    for active_stone in np.where(np.unpackbits(binary_board[player_id, active_board], axis=1))[0]:
                        masks = self.binary_mask_filter(binary_board, player_id, passive_board, passive_stone, active_board, active_stone)
                        all_mask_actions += masks
        return self.binary_mask_sort(binary_board, player_id, all_mask_actions)

    def binary_state_wrapper(self, binary_board:np.ndarray, player_id:int, utility:int, actions:list):
        """Wraps the binary state
        
        Args:
            binary_board (np.ndarray[2,4,uint16]): The binary board
            player_id (int): The player id
            utility (int): The utility of the state
            actions (list(tuple[10](uint16(mask_o), uint16(mask), uint16(mask_r), uint16(mask_p), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone))): The actions

        Returns:
            tuple(np.ndarray[2,4,uint16], int, int, list(tuple[10](uint16(mask_o), uint16(mask), uint16(mask_r), uint16(mask_p), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone))): The wrapped state
        """  
        return (binary_board, player_id, utility, actions)  

    # ---------------------------------------------- #
    # ------------------- Actions ------------------ #

    def binary_apply_action(self, binary_board:np.ndarray, player_id:int, action_mask_tuple:tuple):
        """Applies the action to the binary board

        Args:
            binary_board (np.ndarray[2,4,uint16]): The binary board
            player_id (int): The player id
            action_mask_tuple (tuple[9](uint16(mask_o), uint16(mask), uint16(mask_r), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone)): The action to apply
        Returns:
            np.ndarray[2,4,uint16]: The new binary board
        """
        mask_o, mask, mask_r, direction, length, passive_board, passive_stone, active_board, active_stone = action_mask_tuple
        new_board = binary_board.copy()
        # When passive, only update the old and new positions
        new_board[player_id, passive_board] &= ~mask_o
        new_board[player_id, passive_board] |= mask_r
        # When active, update in a line from the original position to the new position
        new_board[player_id, active_board] &= ~mask_o
        new_board[player_id, active_board] |= mask_r
        new_board[self.next_player(player_id), active_board] &= ~mask
        # Push the stone if needed
        if np.any(binary_board[self.next_player(player_id)] & mask):
            new_board[self.next_player(player_id), active_board] |= mask_r
        return new_board

    def binary_is_terminal(self, binary_board:np.ndarray, player_id:int):
        """Determines if the game is over.
        
        Args:
            binary_board (np.ndarray[2,4,uint16]): The binary board
            player_id (int): The player id

        Returns:
            int: The utility of the game state
        """
        if np.any(binary_board[player_id] == 0):
            return 1
        elif np.any(binary_board[self.next_player(player_id)] == 0):
            return -1
        else:
            return 0

    # ---------------------------------------------- #
    # ------------ Transposition Table ------------- #

    def binary_concat(self, binary_board:np.ndarray):
        """Concatenates the binary board into a string
        
        Args:
            binary_board (np.ndarray[2,4,uint16]): The binary board

        Returns:
            str: The concatenated string
        """
        return "".join([str(quadrant) for quadrant in binary_board])

    def binary_transposition_check(self, binary_board, action, player_id:int):
        '''
        Function used to determine if an action on a certain board will lead to a state that has already been seen

        Args:
            binary_board (np.ndarray[2,4,uint16]): The binary board
            action (tuple[9](uint16(mask_o), uint16(mask), uint16(mask_r), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone)): The action to apply
            player_id (int): The player id

        Returns:
            array : [new_board, player_id, [next_boards_concat1, next_boards_concat2, ...], utility, max_depth, min_depth]
        '''
        # idea -> check if in table, then check new state in table
        board_conc = self.binary_concat(binary_board)
        if (board_conc not in self.binary_transposition_table):
            return None

        newboard = self.binary_apply_action(binary_board, action) # apply the action to the board 

        # Check the new board 
        newboard_conc = self.binary_concat(newboard)
        if (newboard_conc not in self.binary_transposition_table):
            return [newboard, player_id, [], 0, -1, -1]
        
        # Get the information already present in the table
        next_infos_stored = self.binary_transposition_table.get(newboard_conc)

        return next_infos_stored
        
    # Ce qu'il faut stoquer : [board_state_string] (board_state, next_states_list_with_depths, utility)    
    # {"binary_board_concat": [binary_board, player_id, [next_boards_concat1, next_boards_concat2, ...], utility, max_depth, min_depth]}

    def binary_transposition_udpate(self, binary_board, action, player_id:int, utility:int, max_depth:int, min_depth:int):
        '''
        Updates the transposition table with the new information 
        
        Args:
            binary_board (np.ndarray[2,4,uint16]): The binary board
            action (tuple[9](uint16(mask_o), uint16(mask), uint16(mask_r), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone)): The action to apply
            player_id (int): The player id
            utility (int): The utility of the game state
            max_depth (int): The max depth
            min_depth (int): The min depth

        Returns:
            None
        '''
        board_conc = self.binary_concat(binary_board)

        # create the new information to store
        new_info = [binary_board, player_id, [action], utility, max_depth, min_depth]

        # Update the table
        self.binary_transposition_table[board_conc] = new_info

    # ---------------------------------------------- #
    # ------------ Binary Playing :) --------------- #

    def binary_iscutoff(self, binary_board:np.ndarray, player_id:int, depth:int):
        """
        Determines if the search should be cut off at the current depth.
        """
        iscutoff = 1 if self.max_depth == depth else self.binary_is_terminal(binary_board, player_id)
        return iscutoff

    def binary_play(self, binary_board:np.ndarray, player_id:int, remaining_time:float):
        """ Determines the next action to take in the given state :) """
        return self.binary_aplha_beta_search(binary_board, player_id, remaining_time)

    def binary_aplha_beta_search(self, binary_board:np.ndarray, player_id:int, remaining_time:float):
        """
        Applies the alpha-beta search algorithm to find the best action
        """
        action = self.binary_max_value(binary_board, player_id, -float("inf"), float("inf"), 0, remaining_time)
        return action

    def binary_max_value(self, binary_board:np.ndarray, player_id:int, alpha:float, beta:float, depth:int, remaining_time:float):
        """Computes the maximum achievable value for the current player at a given state.

        This method recursively explores all possible actions from the current state to find the one that maximizes
        the player's score.

        Args:
            binary_board (np.ndarray[2,4,uint16]): The current state of the game.
            player_id (int): The player id.
            alpha (float): The best value that the maximizing player can guarantee at the current state.
            beta (float): The best value that the minimizing player can guarantee at the current state.
            depth (int): The current depth in the search tree.
            remaining_time (float): The remaining time in seconds that the agent has to make a decision.

        Returns:
            action to take
        """
        # Check if we have to cut off the search TODO add the time condition 
        if self.binary_iscutoff(binary_board, depth) != 1: # TODO : check if that's the condition we should be checking !
            return self.binary_heuristic_evaluation(binary_board, player_id), None

        max_value = alpha

        actions = self.binary_mask_actions(binary_board, player_id)

        for action in actions:
            test_board = self.binary_apply_action(binary_board, player_id, action)
            test_value, _ = self.binary_min_value(test_board, (player_id + 1) % 2, max_value, beta, depth + 1, remaining_time)

            if test_value > max_value:
                max_value = test_value
                best_action = action

            alpha = max(alpha, max_value)
            if max_value >= beta:
                return max_value, best_action

        return max_value, best_action


    def binary_min_value(self, binary_board:np.ndarray, player_id:int, alpha:float, beta:float, depth:int, remaining_time:float):
        """
        Similar to the max value function, but for the minimizing player score, used to calculate the opponent 
        score.

        Args:
            binary_board (np.ndarray[2,4,uint16]): The current state of the game.
            player_id (int): The player id.
            alpha (float): The best value that the maximizing player can guarantee at the current state.
            beta (float): The best value that the minimizing player can guarantee at the current state.
            depth (int): The current depth in the search tree.
            remaining_time (float): The remaining time in seconds that the agent has to make a decision.

        Returns:
            action to take
        """
        if self.binary_iscutoff(binary_board, depth) != 0:
            return self.binary_heuristic_evaluation(binary_board, player_id), None

        min_value = beta

        actions = self.binary_mask_actions(binary_board, player_id)

        for action in actions:
            test_board = self.binary_apply_action(binary_board, player_id, action)
            test_value, _ = self.binary_max_value(test_board, (player_id + 1) % 2, alpha, min_value, depth + 1, remaining_time)

            if test_value < min_value:
                min_value = test_value
                best_action = action

            beta = min(beta, min_value)
            if min_value <= alpha:
                return min_value, best_action
        
        return min_value, best_action


'''
    def bool_action_wrapper(self, passive_board_id, passive_stone_id, active_board_id, active_stone_id, direction_bool, length):
        return (passive_board_id, passive_stone_id, active_board_id, active_stone_id, direction_bool, length)
    
    def bool_state_wrapper(self, bool_board, player, utility, count_boring_actions, actions):
        return (bool_board, player, utility, count_boring_actions, actions)
    
    def bool_board_wrapper(self):
        return np.zeros((2, 4, 4, 4), dtype=bool)
    
    def bool_position_wrapper(self, x:int=0, y:int=0):
        return np.array([x, y], dtype=int)

    # ---------------------------------------------- #
    # ----------- Shobu Agent Interface ------------ #
    def shobuState2bool(self, state):
        """Converts a ShobuState to a boolean array.

        Args:
            state (ShobuState): The state to convert.

        Returns:
            Tuple: The converted state.
            (bool_board, player, utility, count_boring_actions, actions)
        """
        bool_board = np.zeros((self.num_players, 4, 4, 4), dtype=bool)
        for board_id, board_section in enumerate(state.board):
            for player_id,player in enumerate(board_section):
                for piece in player:
                    row = 3 - (piece // 4)
                    col = piece % 4
                    bool_board[player_id, board_id, row, col] = True
        player = state.to_move
        utility = state.utility
        count_boring_actions = state.count_boring_actions
        return (bool_board, player, utility, count_boring_actions, state.actions) # BAD ACTION

    def shobuAction2boolAction(self, action:tuple):
        passive_board, passive_stone, active_board, active_stone, direction, length = action
        passive_board_id = passive_board
        passive_stone_id = (3 - (passive_stone // 4), passive_stone % 4)
        active_board_id = active_board
        active_stone_id = (3 - (active_stone // 4), active_stone % 4)
        direction_bool = (direction // 4, direction % 4) # I think this is wrong
        return (passive_board_id, passive_stone_id, active_board_id, active_stone_id, direction_bool, length)

    # ---------------------------------------------- #
    # ------------- Transposition Table ------------ #
    transposition_table = dict()
    def transposition_hash(self, bool_board:np.ndarray):
        # Zobrist hashing of a 2,4,4,4 boolean ndarray of a Shobu board
        return hash(bool_board.tostring())
    
    def transposition_lookup(self, bool_board:np.ndarray):
        return self.transposition_table.get(self.transposition_hash(bool_board), None)
    
    def transposition_store(self, bool_board:np.ndarray, value):
        self.transposition_table[self.transposition_hash(bool_board)] = value
   
    # ---------------------------------------------- #
    # ----------------- Move Checking -------------- #

    def next_player(self, player_id:int):
        return 1 - player_id

    def is_valid_move(self, bool_board:np.ndarray, player_id:int, bool_action:tuple):
        # bool_action : (passive_board_id, passive_stone_id, active_board_id, active_stone_id, direction_bool, length)

        # Check if the action is valid
        passive_new_pos = bool_action[1] + bool_action[4]*bool_action[5]
        active_new_pos  = bool_action[3] + bool_action[4]*bool_action[5]
        if any(passive_new_pos <= 0) or any(passive_new_pos >= 3) or any(active_new_pos <= 0) or any(active_new_pos >= 3):
            return False
        passive_board = bool_board[player_id, bool_action[0]]
        active_board = bool_board[player_id, bool_action[2]]
        # Check if the passive board is valid compared to the active board
        if player_id == 0 and bool_action[0] >= 2: # White player's passive board is on black player's side
            return False
        elif player_id == 1 and bool_action[0] < 2: # Black player's passive board is on white player's side
            return False
        # Check if the active board is not aligned with the passive board
        if bool_action[0] % 2 == bool_action[2] % 2:
            return False
        # Check if the passive stone will not push a ennemy stone
        if passive_new_pos in np.where(np.unpackbits(bool_board[self.next_player(player_id), bool_action[0]], axis=1))[0]: # TODO : CHECK IF IT WORKS
            return False
        # Check if the active stone will not push more than one stone
        if active_new_pos in np.where(np.unpackbits(bool_board[player_id, bool_action[2]], axis=1))[0]: # TODO : CHECK IF IT WORKS
            return False
        return True

    # ---------------------------------------------- #
    # ------------ Dynamic Alpha Beta -------------- #

    def dynamic_alpha_beta_search(self, shobu_state:tuple, offset_time:float):
        """Implements the alpha-beta pruning algorithm to find the best action.

        Optimizations :
            - Transposition table
            - Iterative deepening
            - Dynamic Move Ordering
            - Quiescennce search
            - Heuristic evaluation function
            - Killer moves

        Args:
            bool_state: The current game state.

        Returns:
            ShobuAction: The best action as determined by the alpha-beta algorithm.
        """
        bool_state = self.shobuState2bool(shobu_state)
        #print(bool_state[0])
        _, action = self.dynamic_max_value(bool_state, -float("inf"), float("inf"), 0, offset_time)
        return action

    def dynamic_max_value(self, state, alpha = -float("inf"), beta = float("inf"), depth = 0, offset_time = 0):
        
        if self.is_cutoff(state, depth):
            return self.heuristic_evaluation(state, state[1]), None

        max_value = alpha

        for action in self.heuristic_move_generation(state[0], state[1]):
            test_state = self.apply_action(state[0], action)
            test_value, _ = self.dynamic_min_value(test_state, max_value, beta, depth + 1, offset_time)

            if test_value > max_value:
                max_value = test_value
                best_action = action
            
            alpha = max(alpha, max_value)
            if max_value >= beta:
                return max_value, best_action

        return max_value, best_action

    def dynamic_min_value(self, state, alpha = -float("inf"), beta = float("inf"), depth = 0, offset_time = 0):
            
        if self.is_cutoff(state, depth):
            return self.heuristic_evaluation(state, state[1]), None

        min_value = beta

        for action in self.heuristic_move_generation(state[0], state[1]):
            test_state = self.apply_action(state[0], action)
            test_value, _ = self.dynamic_max_value(test_state, alpha, min_value, depth + 1, offset_time)

            if test_value < min_value:
                min_value = test_value
                best_action = action
            
            beta = min(beta, min_value)
            if min_value <= alpha:
                return min_value, best_action

        return min_value, best_action

    def is_cutoff(self, state, depth):
        """Determines if the search should be cut off at the current depth.

        Args:
            state (ShobuState): The current state of the game.
            depth (int): The current depth in the search tree.

        Returns:
            bool: True if the search should be cut off, False otherwise.
        """
        return self.max_depth == depth # or self.game.is_terminal(state)  # HACK : FIX THIS

    def heuristic_quadrant(self, board:np.ndarray, player_id:int, quadrant_id:int):
        """Heuristic evaluation of a quadrant of the board.

        Objective :
            - Defend as much as possible
            - Attack as much as possible
            - If the enemy is close, attack
        """
        number_of_pawns = np.sum(np.unpackbits(board[player_id, quadrant_id], axis=1))
        number_of_enemy_pawns = np.sum(np.unpackbits(board[self.next_player(player_id), quadrant_id], axis=1))
        smallest_distance = 4 # Max distance
        for player_pawn in np.where(np.unpackbits(board[player_id, quadrant_id], axis=1))[0]: # TODO : WILL HAVE TO CHECK
            for enemy_pawn in np.where(np.unpackbits(board[self.next_player(player_id), quadrant_id], axis=1))[0]:
                distance = abs(player_pawn - enemy_pawn)
                if distance < smallest_distance:
                    smallest_distance = distance
        # ---------------------------------------------------------
        score = (5-number_of_pawns)**2 # Defend as much as possible
        score += (5 - number_of_enemy_pawns) # Attack as much as possible
        score += (4-smallest_distance) # if the enemy is close, attack
        return score
    
    def heuristic_evaluation(self, bool_board:np.ndarray, player_id:int):
        # Fuse all heuristic evaluations of the quadrants (We can do here the iterative deepening, using the transposition table)
        score = 0
        for quadrant_id in range(4):
            score += self.heuristic_quadrant(bool_board, player_id, quadrant_id)
        return score

    def heuristic_move_generation(self, bool_board:np.ndarray, player_id:int):
        action_score = []
        best_score = -float('inf')
        # Generate all possible actions for the player
        for passive_board in [0,1] if player_id == 0 else [2,3]:
            for active_board in [1,3] if passive_board in [0,2] else [0,2]:
                # Generate all possible actions for the stones of a board
                for passive_stone in np.where(np.unpackbits(bool_board[1, passive_board], axis=1)):
                    # Generate all possible actions for the stones of the active board
                    for active_stone in np.where(np.unpackbits(bool_board[1, passive_board], axis=1)):
                        # Test all possible directions and lengths
                        for direction in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)]: # 8 directions
                            for length in range(1, 4):
                                action = (passive_board, passive_stone, active_board, active_stone, direction, length)
                                # If the action is valid, evaluate it, and add it to the list
                                if self.is_valid_move(bool_board, player_id, action):
                                    action_and_score = (action, self.heuristic_evaluation(self.apply_action(bool_board, player_id, action, False), player_id))
                                    action_score.append(action_and_score)
                                    best_score = max(best_score, action_and_score[1])

        actions = [action for action,_ in sorted(action_score, key=lambda x: x[1], reverse=True)]
        return actions, best_score
    
    def apply_action(self, bool_board:np.ndarray, player_id:int, bool_action:tuple, generate_new_moves:bool=True):
        new_board = bool_board.copy()
        passive_new_pos = bool_action[1] + bool_action[3]*bool_action[4]
        active_new_pos  = bool_action[3] + bool_action[3]*bool_action[4]
        # When passive, only update the old and new positions
        new_board[player_id, bool_action[0], bool_action[1]] = False
        new_board[player_id, bool_action[2], passive_new_pos] = True
        # When active, update in a line from the original position to the new position
        for distance in range(0, bool_action[5]):
            new_board[player_id, bool_action[2], bool_action[3] + distance*bool_action[4]] = False
        new_board[player_id, bool_action[2], active_new_pos] = True
        # Generate new moves if needed
        if generate_new_moves:
            new_moves = self.heuristic_move_generation(new_board, player_id)
        else:
            new_moves = []
        return (new_board, self.next_player(player_id), 0, 0, new_moves)
'''

'''
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
'''
'''binary_rep = self.shobuState_to_binary_rep(state.board)
    self.print_binary_rep(binary_rep)
    print(self.get_number_of_pawns(binary_rep))

    data = (self.bool_array_to_binary_array(self.shobuState_to_bool_array(state.board)))
    print(self.shobuState_to_bool_array(state.board))

    print( self.binary_array_to_bool_array(binary_rep))

    for plate in range(2):
        for board in range(4):
            cell_int16 = binary_rep[plate, board]
            cells = np.unpackbits(np.array([cell_int16], dtype=np.uint16).view(np.uint8), bitorder='little').reshape(4,4)
            print(cells)'''

### BINARY ENCODING :
"""
To count the number of pawns in a quadrant, we can use the following code :
    np.sum(np.unpackbits(np.array([board_state], dtype=np.uint16).view(np.uint8)))

To check if a move will intersect, we can use the following code :
    if board_ennemy & move_mask(diagonals, lines, ...) :
        return False
    
To pre generate all possible masks for a pawn : 
    masks = np.zeros((4,4,8), dtype=np.uint16) # 4 length (X) x 4 length (Y) x 8 directions (4 cardinal + 4 diagonals) x 16 bits --> Maximise encoding/decoding
    mask_results = np.zeros((4,4,8), dtype=np.uint16) # 4 length (X) x 4 length (Y) x 8 directions (4 cardinal + 4 diagonals) x 16 bits --> Maximise encoding/decoding
    directions = np.array([(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)])
    for x in range(4):
        for y in range(4):
            for direction_id, direction in enumerate(directions):
                mask = 0
                result = 0
                for length in range(1, 5):
                    new_x = x + length*direction[0]
                    new_y = y + length*direction[1]
                    if new_x < 0 or new_x >= 4 or new_y < 0 or new_y >= 4:
                        break
                    mask |= 1 << (15 - 4*new_x - new_y)
                    result |= 1 << (15 - 4*x - y)
                masks[x,y,direction_id] = mask
                mask_results[x,y,direction_id] = result
    return masks, mask_results, directions

To filter the masks :
==> INPUT : masks, mask_results, directions, board_ennemy, board_player, stone_passive, stone_active, board_passive, board_active

    # WARNING : 2 baords must be checked, the passive board and the active board
    if stone_passive >= 16 or stone_active >= 16: # 4x4 board
        return []
    if board_passive >= 4 or board_active >= 4: # 2x2 boards
        return []
    if board_passive % 2 == board_active % 2: # The boards must be on different sides
        return []

    if player_id == 0 and board_passive >= 2: # White player's passive board is on black player's side
        return []
    elif player_id == 1 and board_passive < 2: # Black player's passive board is on white player's side
        return []

    # Check if the passive stone will not push a ennemy stone
    if np.any(board_ennemy & masks[stone_passive, board_passive]):
        return []
    # Check if the active stone will not push more than one stone
    if np.any(board_player & masks[stone_active, board_active]):
        return []
    return mask_results[stone_active, board_active]

"""