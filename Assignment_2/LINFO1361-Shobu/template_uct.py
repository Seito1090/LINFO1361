from agent import Agent
import random
import math

class Node:
    """Node Class

    A node in the MCTS tree.

    Attributes:
        parent (Node): The parent node of this node.
        state (ShobuState): The game state represented by this node.
        U (int): The total reward of the node. 
        N (int): The number of times the node has been visited.
        children (dict[Node, ShobuAction]): A dictionary mapping child nodes to their corresponding actions that lead to the state they represent.
    """
    def __init__(self, parent, state):
        """Initializes a new Node object.

        Args:
            parent (Node): The parent node of this node.
            state (ShobuState): The game state represented by this node.
        """
        self.parent = parent
        self.state = state
        self.U = 0
        self.N = 0
        self.children = {}

class UCTAgent(Agent):
    """An agent that uses the UCT algorithm to determine the best move.

    This agent extends the base Agent class, providing an implementation of the play
    method that utilizes UCT version of the MCTS algorithm.

    Attributes:
        player (int): The player id this agent represents.
        game (ShobuGame): The game the agent is playing.
        iteration (int): The number of simulations to perform in the UCT algorithm.
    """

    def __init__(self, player, game, iteration):
        """Initializes a UCTAgent with a specified player, game, and number of iterations.

        Args:
            player (int): The player id this agent represents.
            game (ShobuGame): The game the agent is playing.
            iteration (int): The number of simulations to perform in the UCT algorithm.
        """
        super().__init__(player, game)
        self.iteration = iteration

    def play(self, state, remaining_time):
        """Determines the next action to take in the given state.

        Args:
            state (ShobuState): The current state of the game.
            remaining_time (float): The remaining time in seconds that the agent has to make a decision.

        Returns:
            ShobuAction: The chosen action.
        """
        return self.uct(state)

    def uct(self, state):
        """Executes the UCT algorithm to find the best action from the current state.

        Args:
            state (ShobuState): The current state of the game.

        Returns:
            ShobuAction: The action leading to the best-perceived outcome based on UCT algorithm.
        """
        root = Node(None, state)
        root.children = { Node(root, self.game.result(root.state, action)): action for action in self.game.actions(root.state) }
        for _ in range(self.iteration):
            leaf = self.select(root)
            child = self.expand(leaf)
            result = self.simulate(child.state)
            self.back_propagate(result, child)
        max_state = max(root.children, key=lambda n: n.N)
        return root.children.get(max_state)

    def select(self, node):
        """Selects a leaf node using the UCB1 formula to maximize exploration and exploitation.

        The function recursively selects the children of the node that maximise the UCB1 score, exploring the most promising 
        path in the game tree. It stops when a leaf is found and returns it. A leaf is either a node in a terminal state, 
        or a node with a child for which no simulation has yet been performed.
        
        Args:
            node (Node): The node to select from.

        Returns:
            Node: The selected leaf node.
        """
        while node.children:
            unexplored_children = [child for child in node.children if child.N == 0]
            if unexplored_children:
                return node
            ucb1_values = {child: self.UCB1(child) for child in node.children}
            max_child = max(ucb1_values, key=ucb1_values.get)
            node = max_child
        return node
    
    def expand(self, node):
        """Expands a node by adding a child node to the tree for an unexplored action.

        The function returns one of the children of the node for which no simulation has yet been performed. 
        In addition, the function must initialize all the children of that child node in the child's "children" dictionary. 
        If the node is in a terminal state, the function returns itself, indicating that the node can no longer be expanded.

        Args:
            node (Node): The node to expand. This node represents the current state from which we want to explore possible actions.

        Returns:
            Node: The child node selected. If the node is at a terminal state, the node itself is returned.
        """
        if self.game.is_terminal(node.state) or not self.game.actions(node.state):
            return node

        unexplored_actions = [action for action in self.game.actions(node.state) if action not in node.children.values()]
        if not unexplored_actions:
            return node

        selected_action = random.choice(unexplored_actions)

        new_state = self.game.result(node.state, selected_action)
        new_node = Node(node, new_state)

        new_node.children = { Node(new_node, self.game.result(new_node.state, action)): action for action in self.game.actions(new_node.state) }

        return new_node

    def simulate(self, state):
        """Simulates a random play-through from the given state to a terminal state.

        Args:
            state (ShobuState): The state to simulate from.

        Returns:
            float: The utility value of the resulting terminal state in the point of view of the opponent in the original state.
        """
        current_state = state
        max_rounds = 5
        rounds = 0

        while not self.game.is_terminal(current_state) and rounds < max_rounds:
            action = random.choice(self.game.actions(current_state))
            current_state = self.game.result(current_state, action)
            rounds += 1

        return self.game.utility(current_state, (state.to_move+1) % 2)

    def back_propagate(self, result, node):
        """Propagates the result of a simulation back up the tree, updating node statistics.

        This method is responsible for updating the statistics for each node according to the result of the simulation. 
        It recursively updates the U (utility) and N (number of visits) values for each node on the path from the given 
        node to the root. The utility of a node is only updated if it is a node that must contain the win rate of the 
        player who won the simulation, otherwise the utility is not modified.

        Args:
            result (float): The result of the simulation.
            node (Node): The node to start backpropagation from.
        """
        node.N += 1  # Increment visit count

        if result == 1:  # The player won
            node.U += 1

        # If the node has a parent, recursively propagate the result to the parent node
        if node.parent is not None:
            self.back_propagate(result, node.parent)

    def UCB1(self, node):
        """Calculates the UCB1 value for a given node.

        Args:
            node (Node): The node to calculate the UCB1 value for. 

        Returns:
            float: The UCB1 value of the node. Returns infinity if the node has not been visited yet.
        """

        # formula for UCB1 : U(n) / N(n) + c * sqrt(logN(Parent(n)) / N(n))
        c = math.sqrt(2)
        if node.N == 0:
            return float('inf')
        else:
            return node.U / node.N + c * math.sqrt(math.log(node.parent.N) / node.N)