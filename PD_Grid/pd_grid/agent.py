import mesa
import numpy as np


class PDAgent(mesa.Agent):
    """Agent member of the iterated, spatial prisoner's dilemma model."""

    def __init__(self, pos, model, starting_move=None, initial_weights = None, actions = ['C','D'], eta = 0.1):
        """
        Create a new Prisoner's Dilemma agent.

        Args:
            pos: (x, y) tuple of the agent's position.
            model: model instance
            starting_move: If provided, determines the agent's initial state:
                           C(ooperating) or D(efecting). Otherwise, random.
        """
        super().__init__(pos, model)
        self.pos = pos
        self.score = 0

        # # change this maybe?
        # if starting_move:
        #     self.move = starting_move
        # else:
        self.move_i = np.arange(len(actions))
        self.move = self.random.choice(self.move_i)
        self.next_move = None
        



        if initial_weights is None:
            self.w = np.ones(len(actions))
        else:
            self.w = initial_weights

        self.eta = eta
        self.actions = actions

    @property
    def isAction0(self):
        # return whether the agent cooperates more than it defects
        return self.w[0] >= self.w[1]
        # return self.move == "C"

    @property
    def action0Weight(self):
        return self.w[0]/(np.sum(self.w))


    def step(self):
        # """Get the best neighbor's move, and change own move accordingly if better than own score."""
        # neighbors = self.model.grid.get_neighbors(self.pos, True, include_center=True)
        # best_neighbor = max(neighbors, key=lambda a: a.score)
        # self.next_move = best_neighbor.move
        self.next_move = np.random.choice(self.move_i, p = self.w/np.sum(self.w))

        if self.model.schedule_type != "Simultaneous":
            self.advance()

    def advance(self):
        self.move = self.next_move
        payoffs = self.calculate_payoffs()
        # print('score', self.score)
        # print('pyf', payoffs)
        # print('move', self.move)
        self.score += payoffs[self.move]
        self.update_weights(payoffs)
        
    def update_weights(self, payoffs):
        self.w = self.w * np.exp(self.eta * payoffs)        

    # returns vector of payoffs for all possible actions
    def calculate_payoffs(self):
        payoffs = np.zeros_like(self.move_i)

        neighbors = self.model.grid.get_neighbors(self.pos, moore = self., True)
        if self.model.schedule_type == "Simultaneous":
            moves = [neighbor.next_move for neighbor in neighbors]
        else:
            moves = [neighbor.move for neighbor in neighbors]

        for i in range(len(payoffs)):
            payoffs[i] = sum(self.model.payoff[(self.actions[i], self.actions[move])] for move in moves)

        return payoffs
