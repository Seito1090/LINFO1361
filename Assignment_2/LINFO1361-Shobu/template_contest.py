from agent import Agent
import random
import numpy as np
import time

def hot_timer_custom(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:e} seconds to execute.")
        return result
    return wrapper

class AI(Agent):
    """An agent that plays following your algorithm.

    This agent extends the base Agent class, providing an implementation your agent.

    Attributes:
        player (int): The player id this agent represents.
        game (ShobuGame): The game the agent is playing.
    """

    # ---------------------------------------------- #
    # ------------- Shobu Agent Logic -------------- #
    
    num_players = 2
    max_depth = 2
    mask_object = None
    binary_transposition_table = None

    def __init__(self, player, state):
        self.binary_transposition_table = dict()
        self.mask_object = self.BinaryMasks()

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

        '''
        for x in range(4):
            for y in range(4):
                for direction_id in range(8):
                    for length in range(1,4):
                        self.print_mask(self.mask_object.masks[x,y,direction_id,length] | self.mask_object.mask_origins[x,y,direction_id])
                        print(f"xy:{x},{y} | dir: {self.mask_object.directions[direction_id]} | leng: {length}-------------------------------------------------")
        '''

        # Simulations to find the best action
        best_action_idx = self.binary_aplha_beta_search(binary_state, remaining_time + time.time())

        if best_action_idx is None:
            return None
        return state.actions[int(best_action_idx)]

    # ---------------------------------------------- #
    # -------------- Shobu to Binary --------------- #
    def next_player(self, player_id:int):
        return 1 - player_id

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
            list(tuple[8](tuple[2](xy_passive), tuple[2](xy_active), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone)): The converted action.
        """
        actions = []
        # For every action
        for action in shobu_action:
            passive_board, passive_stone, active_board, active_stone, direction, length = action

            dir_true = np.zeros(2)
            if direction > 1:
                dir_true[1] = 1
            elif direction < -1:
                dir_true[1] = -1
            
            if direction in [3,-1,-5]:
                dir_true[0] = -1
            elif direction in [1,5,-3]:
                dir_true[0] = 1

            direction_idx = np.where(np.all(self.mask_object.directions == dir_true, axis=1))[0][0]

            mask_o_passive = 1 << passive_stone
            mask_o_active = 1 << active_stone

            mask_passive = 0
            mask_active = 0
            for i in range(1, length+1):
                mask_passive |= 1 << (passive_stone + i*direction)
                mask_active |= 1 << (active_stone + i*direction)

            position_mask_o_passive = np.where(self.mask_object.mask_origins == mask_o_passive)
            position_mask_o_active = np.where(self.mask_object.mask_origins == mask_o_active)

            xy_passive = (position_mask_o_passive[0][0], position_mask_o_passive[1][0])
            xy_active = (position_mask_o_active[0][0], position_mask_o_active[1][0])

            actions.append((xy_passive, xy_active, direction_idx, length, passive_board, passive_stone, active_board, active_stone))

        return actions

    def print_binary_board(self, binary_board:np.ndarray):
        """Prints the binary board

        Args:
            binary_board (np.ndarray[2,4,uint16]): The binary board        
        """
        print("\tWhite : ◉ \n\tBlack : ◎ \n\tEmpty : ▢")

        output_string = ["" for _ in range(9)]
        output_string[4] = "-----------------"*2
        for line_id in range(8):
            true_line_id = line_id + line_id // 4
            for quadrant_id in [2,3] if line_id >= 4 else [0,1]:
                for bit_in_quad in range(4):
                    white = (binary_board[0,quadrant_id] >> ((line_id % 4)*4 + bit_in_quad)) & 1
                    black = (binary_board[1,quadrant_id] >> ((line_id % 4)*4 + bit_in_quad)) & 1
                    if white:
                        output_string[true_line_id] += "◉ "
                    elif black:
                        output_string[true_line_id] += "◎ "
                    else:
                        output_string[true_line_id] += "▢ "
                output_string[true_line_id] += "|"

        for line in output_string[::-1]:
            print(line)           

    def print_mask(self, mask:np.uint16):
        """Prints the mask

        Args:
            mask (np.uint16): The mask to print
        """
        lines = ["" for _ in range(4)]
        for i in range(4):
            for j in range(4):
                lines[i] += str((mask >> (4*i + j)) & 1) + " "
        for line in lines[::-1]:
            print(line)

    def print_mask_action(self, xy_action:tuple, direction:int, length:int):
        """Prints the mask action
        
        Args:
            xy_action (tuple[2](int, int)): The action
        """
        lines = ["\t" for _ in range(4)]
        for mask in [self.mask_object.mask_origins[xy_action[0], xy_action[1], direction],
                      self.mask_object.masks[xy_action[0], xy_action[1], direction, length],
                        self.mask_object.mask_results[xy_action[0], xy_action[1], direction, length],
                          self.mask_object.mask_push_result[xy_action[0], xy_action[1], direction, length]]:
            for i in range(4):
                for j in range(4):
                    lines[i] += str((mask >> (4*i + j)) & 1) + " "
                lines[i] += "|\t"
        print("\tOrigin\t\tMask\t\tResult\t\tPush")
        for line in lines[::-1]:
            print(line)

    def print_actions_masks(self, actions:list):
        """Prints the actions masks
        
        Args:
            actions (list(tuple[8](tuple[2](xy_passive), tuple[2](xy_active), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone)): The actions
        """
        for action in actions:
            print(f"Passive board : {action[4]} -> Active board : {action[6]}")
            print(f"Passive stone : {action[5]} -> Active stone : {action[7]}")
            print(f"Direction : {self.mask_object.directions[action[2]]} -> Length : {action[3]}")
            print("Mask Passive : ")
            self.print_mask_action(action[0], action[2], action[3])
            print("Mask Active: ")
            self.print_mask_action(action[1], action[2], action[3])

    # ----------------------------------------------- #
    # ----------------- Binary Masks ---------------- #

    class BinaryMasks:
        directions = np.array([(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)])
        masks = np.zeros((4,4,8,4), dtype=np.uint16) # Mask of the move to clear it all, and check where you arrive (has the resulting position, but not the origin)
        mask_results = np.zeros((4,4,8,4), dtype=np.uint16) # Mask for only the resulting position of the stone
        mask_origins = np.zeros((4,4,8), dtype=np.uint16) # Mask for only the original position of the stone
        mask_push_result = np.zeros((4,4,8,4), dtype=np.uint16) # Mask for only the pushed stone
        def __init__(self):
            """Generates all masks needed for the binary representation of the board
            Must only be called once, and the masks must be stored in a variable
            """
            for x in range(4):
                for y in range(4):
                    for direction_id, direction in enumerate(self.directions):
                        origin = 1 << (x + 4*y)
                        for length in range(1, 4): # Length 0 is the origin, so we start at 1
                            new_x = x + length*direction[0]
                            new_y = y + length*direction[1]
                            if new_x < 0 or new_x >= 4 or new_y < 0 or new_y >= 4:
                                continue
                            # Masking Trailing
                            for i in range(1, length+1):
                                self.masks[x,y,direction_id,length] |= 1 << (x + i*direction[0] + 4*(y + i*direction[1]))
                            # Masking Result
                            self.mask_results[x,y,direction_id,length] = 1 << (new_x + 4*new_y)
                            # Pushing
                            if new_x + direction[0] >= 0 and new_x + direction[0] < 4 and new_y + direction[1] >= 0 and new_y + direction[1] < 4:
                                self.mask_push_result[x,y,direction_id,length] = 1 << ((new_x + direction[0]) + 4*(new_y + direction[1]))
                        # Mark the origin
                        self.mask_origins[x,y,direction_id] = origin
        
        def next_player(self, player_id:int):
            return 1 - player_id

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
                list(tuple[8](tuple[2](xy_passive), tuple[2](xy_active), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone)): The filtered masks
            """
            x_passive = passive_stone % 4
            y_passive = passive_stone // 4
            x_active = active_stone % 4
            y_active = active_stone // 4
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
            # Check if the passive stone will not push a ennemy stone
            for direction_id in range(8):
                for length_id in range(1, 3):
                    # Check if the mask is void
                    if self.masks[x_passive, y_passive, direction_id, length_id] == 0:
                        continue
                    # Check if the path is clear as a passive stone
                    if binary_board[ennemy_player_id, passive_board] & self.masks[x_passive, y_passive, direction_id, length_id] \
                        or binary_board[player_id, passive_board] & self.masks[x_passive, y_passive, direction_id, length_id]:
                        continue
                    # Check that the new position is valid
                    x_new_passive = x_passive + length_id*self.directions[direction_id][0]
                    y_new_passive = y_passive + length_id*self.directions[direction_id][1]
                    x_new_active = x_active + length_id*self.directions[direction_id][0]
                    y_new_active = y_active + length_id*self.directions[direction_id][1]
                    if x_new_passive < 0 or x_new_passive >= 3 or y_new_passive < 0 or y_new_passive >= 3 \
                        or x_new_active < 0 or x_new_active >= 3 or y_new_active < 0 or y_new_active >= 3:
                        continue
                    # Check that the stone can attack (not more than 1 stone), and that if you push a stone, it is valid
                    ennemy_on_path = (self.mask_push_result[x_active, y_active, direction_id, length_id] & self.masks[x_active, y_active, direction_id, length_id])
                    ally_on_path = (self.mask_push_result[x_active, y_active, direction_id, length_id] & self.masks[x_active, y_active, direction_id, length_id])
                    push_block_ennemy = ennemy_on_path | (self.mask_push_result[x_active, y_active, direction_id, length_id] & binary_board[ennemy_player_id, active_board])
                    push_block_ally   = ennemy_on_path | (self.mask_push_result[x_active, y_active, direction_id, length_id] & binary_board[player_id, active_board])
                    check_push_block = push_block_ennemy.bit_count() > 1 or push_block_ally.bit_count() > 1 or ally_on_path.bit_count() > 1

                    check_collision_player = (binary_board[player_id, active_board] & self.masks[x_active, y_active, direction_id, length_id]) != 0

                    if check_push_block or check_collision_player:
                        continue
                    ellement = ((x_passive, y_passive),
                                (x_active, y_active),
                                direction_id,
                                length_id,
                                passive_board,
                                passive_stone,
                                active_board,
                                active_stone)
                    masked_results.append(ellement)
            return masked_results

        def binary_mask_actions(self, binary_board:np.ndarray, player_id:int, is_for_min:bool=False):
            """Generates all the possible actions for a player
            
            Args:
                binary_board (np.ndarray[2,4,uint16]): The binary board
                player_id (int): The player id

            Returns:
                list(tuple[8](tuple[2](xy_passive), tuple[2](xy_active), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone)): The actions
            """
            all_mask_actions = []
            for passive_board in [0,1] if player_id == 0 else [2,3]:
                for active_board in [1,3] if passive_board in [0,2] else [0,2]:
                    for passive_stone in self.binary_number_to_where(binary_board[player_id, passive_board]):
                        for active_stone in self.binary_number_to_where(binary_board[player_id, active_board]):
                            masks = self.binary_mask_filter(binary_board, player_id, passive_board, passive_stone, active_board, active_stone)
                            all_mask_actions += masks
            return self.binary_mask_sort(binary_board, player_id, all_mask_actions, is_for_min)

        def binary_mask_sort(self, binary_board:np.ndarray, player_id:int, actions:list, is_for_min:bool=False):
            """Sorts the actions based on a heuristic
            
            Args:
                binary_board (np.ndarray[2,4,uint16]): The binary board
                player_id (int): The player id
                actions (list(tuple[8](tuple[2](xy_passive), tuple[2](xy_active), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone))): The actions to sort

            Returns:
                list(tuple[8](tuple[2](xy_passive), tuple[2](xy_active), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone)): The sorted actions
            """
            scoring_array = np.zeros(len(actions))
            for action_id, action in enumerate(actions):
                scoring_array[action_id] = self.binary_heuristic_evaluation(self.binary_apply_action(binary_board, player_id, action), player_id)
            return [actions[i] for i in np.argsort(scoring_array, kind='quicksort')[::-1]]

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
            
            number_of_pawns = (binary_board[player_id, quadrant_id]).bit_count()
            number_of_enemy_pawns = (binary_board[self.next_player(player_id), quadrant_id]).bit_count()
            smallest_distance = 4
            #==> TOO SLOW
            #for player_pawn in self.binary_number_to_where(binary_board[player_id, quadrant_id]):
            #    for enemy_pawn in self.binary_number_to_where(binary_board[self.next_player(player_id), quadrant_id]):
            #        distance = abs(player_pawn - enemy_pawn)
            #        if distance < smallest_distance:
            #            smallest_distance = distance
            # ---------------------------------------------------------
            score = (number_of_pawns) # Defend as much as possible
            score += (5 - number_of_enemy_pawns)**2 # Attack as much as possible
            #score += (4-smallest_distance) # if the enemy is close, attack
            if number_of_enemy_pawns == 1:
                score *= 10
            return score

        def binary_number_to_array(self, number:int, size:int = 16):
            """Converts a number to an array
            
            Args:
                number (int): The number to convert

            Returns:
                np.ndarray[4]: The array
            """
            return np.array([number >> i & 1 for i in range(size)])

        def binary_number_to_where(self, number:int, size:int = 16):
            """Converts a number to a where
            
            Args:
                number (int): The number to convert

            Returns:
                np.ndarray[4]: The array
            """
            return np.where(self.binary_number_to_array(number, size))[0]

        def binary_apply_action(self, binary_board:np.ndarray, player_id:int, action_mask_tuple:tuple):
            """Applies the action to the binary board

            Args:
                binary_board (np.ndarray[2,4,uint16]): The binary board
                player_id (int): The player id
                action_mask_tuple (tuple[8](tuple[2](xy_passive), tuple[2](xy_active), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone)): The action to apply
            Returns:
                np.ndarray[2,4,uint16]: The new binary board
            """
            new_board = binary_board.copy()
            xy_passive, xy_active, direction, length, passive_board, passive_stone, active_board, active_stone = action_mask_tuple
            # Delete the old positions, and place at new for passive
            new_board[:, passive_board] &= ~self.mask_origins[xy_passive[0], xy_passive[1], direction]
            new_board[player_id, passive_board] |= self.mask_results[xy_passive[0], xy_passive[1], direction, length]
            # Delete the old positions, delete the path, and place at new for active (player), and push the stone if needed
            new_board[:, active_board] &= ~self.mask_origins[xy_active[0], xy_active[1], direction]
            new_board[:, active_board] &= ~self.masks[xy_active[0], xy_active[1], direction, length]
            new_board[player_id, active_board] |= self.mask_results[xy_active[0], xy_active[1], direction, length]
            if length+1 <3 and (binary_board[self.next_player(player_id), active_board] & self.masks[xy_active[0], xy_active[1], direction, length]):
                new_board[self.next_player(player_id), active_board] |= self.mask_push_result[xy_active[0], xy_active[1], direction, length]
            return new_board

    def binary_state_wrapper(self, binary_board:np.ndarray, player_id:int, utility:int, actions:list):
        """Wraps the binary state
        
        Args:
            binary_board (np.ndarray[2,4,uint16]): The binary board
            player_id (int): The player id
            utility (int): The utility of the state
            actions (list(tuple[8](tuple[2](xy_passive), tuple[2](xy_active), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone))): The actions

        Returns:
            tuple(np.ndarray[2,4,uint16], int, int, list(tuple[10](uint16(mask_o), uint16(mask), uint16(mask_r), uint16(mask_p), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone))): The wrapped state
        """  
        return (binary_board, player_id, utility, actions)  

    # ---------------------------------------------- #
    # ------------------- Actions ------------------ #

    def binary_apply_action_to_state(self, binary_board:np.ndarray, player_id:int, action_mask_tuple:tuple, is_for_min:bool=False):
        """Applies the action to the binary board

        Args:
            binary_board (np.ndarray[2,4,uint16]): The binary board
            player_id (int): The player id (of that board)
            action (tuple[8](tuple[2](xy_passive), tuple[2](xy_active), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone)): The action to apply

        Returns:
            np.ndarray[2,4,uint16]: The new binary board
        """
        new_board = self.mask_object.binary_apply_action(binary_board, player_id, action_mask_tuple)
        #self.print_actions_masks([action_mask_tuple])
        #print("Player : ", player_id)
        #self.print_binary_board(new_board)
        new_to_move = self.next_player(player_id)
        new_utility = self.binary_is_terminal(new_board, new_to_move) # UTILITY
        new_actions = self.mask_object.binary_mask_actions(new_board, new_to_move, is_for_min)
        return (new_board, new_to_move, new_utility, new_actions)


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
            action (tuple[10](uint16(mask_o), uint16(mask), uint16(mask_r), uint16(mask_p), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone)): The action to apply
            player_id (int): The player id

        Returns:
            array : [new_board, player_id, [next_boards_concat1, next_boards_concat2, ...], utility, max_depth, min_depth]
        '''
        # idea -> check if in table, then check new state in table
        board_conc = self.binary_concat(binary_board)
        if (board_conc not in self.binary_transposition_table):
            return None

        newboard = self.mask_object.binary_apply_action(binary_board, action) # apply the action to the board 

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
            action (tuple[10](uint16(mask_o), uint16(mask), uint16(mask_r), uint16(mask_p), int(direction), int(length), int(passive_board), int(passive_stone), int(active_board), int(active_stone)): The action to apply
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
        iscutoff = 1 if self.max_depth <= depth else self.binary_is_terminal(binary_board, player_id)
        return iscutoff

    def binary_aplha_beta_search(self, binary_state:tuple, remaining_time:float):
        """
        Applies the alpha-beta search algorithm to find the best action
        """
        value, action_id = self.binary_max_value(binary_state, -float("inf"), float("inf"), 0, remaining_time)
        return action_id

    def binary_max_value(self, binary_state:tuple, alpha:float, beta:float, depth:int, remaining_time:float):
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
        binary_board, player_id, _, actions = binary_state
        # Check if we have to cut off the search TODO add the time condition 
        if self.binary_iscutoff(binary_board, player_id, depth): # TODO : HACKcheck if that's the condition we should be checking !
            return self.mask_object.binary_heuristic_evaluation(binary_board, player_id), 0

        best_action_id = 0
        max_value = float("-inf") 
        for action_id, action in enumerate(binary_state[3]):
            if remaining_time - time.time() < 0:
                return max_value, 0
            test_state = self.binary_apply_action_to_state(binary_board, player_id, action, is_for_min=True)
            test_value, _ = self.binary_min_value(test_state, alpha, beta, depth + 1, remaining_time)

            #print("Max value : ", max_value, " | Alpha : ", alpha, " | Beta : ", beta)

            if test_value > max_value:
                max_value = test_value
                best_action_id = action_id
            
            alpha = max(alpha, max_value)
            if max_value >= beta:
                return max_value, best_action_id
        return max_value, best_action_id


    def binary_min_value(self, binary_state:tuple, alpha:float, beta:float, depth:int, remaining_time:float):
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
            
        binary_board, player_id, _, actions = binary_state
        # Check if we have to cut off the search TODO add the time condition 
        if self.binary_iscutoff(binary_board, player_id, depth):
            return self.mask_object.binary_heuristic_evaluation(binary_board, player_id), 0

        best_action_id = 0
        min_value = float("inf") 
        for action_id, action in enumerate(binary_state[3]):
            if remaining_time - time.time() < 0:
                return min_value, 0
            test_state = self.binary_apply_action_to_state(binary_board, player_id, action)
            test_value, _ = self.binary_max_value(test_state, alpha, beta, depth + 1, remaining_time)

            #print("Min value : ", min_value, " | Alpha : ", alpha, " | Beta : ", beta)

            if test_value < min_value:
                min_value = test_value
                best_action_id = action_id

            beta = min(beta, min_value)
            if min_value <= alpha:
                return min_value, best_action_id

        return min_value, best_action_id
