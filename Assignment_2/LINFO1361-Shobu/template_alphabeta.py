from agent import Agent

class AlphaBetaAgent(Agent):
    """An agent that uses the alpha-beta pruning algorithm to determine the best move.

    This agent extends the base Agent class, providing an implementation of the play
    method that utilizes the alpha-beta pruning technique to make decisions more efficiently.

    Attributes:
        max_depth (int): The maximum depth the search algorithm will explore.
    """

    def __init__(self, player, game, max_depth):
        """Initializes an AlphaBetaAgent instance with a specified player, game, and maximum search depth.

        Args:
            player (int): The player ID this agent represents (0 or 1).
            game (ShobuGame): The Shobu game instance the agent will play on.
            max_depth (int): The maximum depth of the search tree.
        """
        super().__init__(player, game)
        self.max_depth = max_depth

    def play(self, state, remaining_time):
        """Determines the best action by applying the alpha-beta pruning algorithm.

        Overrides the play method in the base class.

        Args:
            state (ShobuState): The current state of the game.
            remaining_time (float): The remaining time in seconds that the agent has to make a decision.

        Returns:
            ShobuAction: The action determined to be the best by the alpha-beta algorithm.
        """
        return self.alpha_beta_search(state)
    
    def is_cutoff(self, state, depth):
        """Determines if the search should be cut off at the current depth.

        Args:
            state (ShobuState): The current state of the game.
            depth (int): The current depth in the search tree.

        Returns:
            bool: True if the search should be cut off, False otherwise.
        """
        return self.max_depth == depth or self.game.is_terminal(state)
    
    def eval(self, state):
        """Evaluates the given state and returns a score from the perspective of the agent's player.

        Args:
            state (ShobuState): The game state to evaluate.

        Returns:
            float: The evaluated score of the state.
        """
        min_stones_white = 4
        min_stones_black = 4

        # Just did what the pdf said
        for singleBoard in range(4):
            white_stones, black_stones = state.board[singleBoard]
            if len(white_stones) < min_stones_white:
                min_stones_white = len(white_stones)
            if len(black_stones) < min_stones_black:
                min_stones_black = len(black_stones)

        # To make the relative score on the player id (0 or 1)
        if self.player == 0:
            score = (min_stones_white - min_stones_black) / 1.0
        else:
            score = (min_stones_black - min_stones_white) / 1.0
        
        return score

    def alpha_beta_search(self, state):
        """Implements the alpha-beta pruning algorithm to find the best action.

        Args:
            state (ShobuState): The current game state.

        Returns:
            ShobuAction: The best action as determined by the alpha-beta algorithm.
        """
        _, action = self.max_value(state, -float("inf"), float("inf"), 0)
        return action

    def max_value(self, state, alpha, beta, depth):
        """Computes the maximum achievable value for the current player at a given state using the alpha-beta pruning.

        This method recursively explores all possible actions from the current state to find the one that maximizes
        the player's score, pruning branches that cannot possibly affect the final decision.

        Args:
            state (ShobuState): The current state of the game.
            alpha (float): The current alpha value, representing the minimum score that the maximizing player is assured of.
            beta (float): The current beta value, representing the maximum score that the minimizing player is assured of.
            depth (int): The current depth in the search tree.

        Returns:
            tuple: A tuple containing the best value achievable from this state and the action that leads to this value.
                If the state is a terminal state or the depth limit is reached, the action will be None.
        """

        if self.is_cutoff(state, depth):
            return self.eval(state), None

        max_val = -float("inf") 

        for action in self.game.actions(state):
            test_state = self.game.result(state, action)
            test_value, _ = self.min_value(test_state, alpha, beta, depth + 1)

            if test_value > max_val:
                max_val = test_value
                return_action = action

            alpha = max(alpha, max_val)
            if max_val >= beta:
                return max_val, return_action

        return max_val, return_action


    def min_value(self, state, alpha, beta, depth):
        """Computes the minimum achievable value for the opposing player at a given state using the alpha-beta pruning.

        Similar to max_value, this method recursively explores all possible actions from the current state to find
        the one that minimizes the opponent's score, again using alpha-beta pruning to cut off branches that won't
        affect the outcome.

        Args:
            state (ShobuState): The current state of the game.
            alpha (float): The current alpha value, representing the minimum score that the maximizing player is assured of.
            beta (float): The current beta value, representing the maximum score that the minimizing player is assured of.
            depth (int): The current depth in the search tree.

        Returns:
            tuple: A tuple containing the best value achievable from this state for the opponent and the action that leads to this value.
                If the state is a terminal state or the depth limit is reached, the action will be None.
        """
        if self.is_cutoff(state, depth):
            return self.eval(state), None

        min_val = float("inf") 

        for action in self.game.actions(state):
            test_state = self.game.result(state, action)
            test_value, _ = self.max_value(test_state, alpha, beta, depth + 1)

            if test_value < min_val:
                min_val = test_value
                return_action = action

            beta = min(beta, min_val)
            if min_val <= alpha:
                return min_val, return_action

        return min_val, return_action