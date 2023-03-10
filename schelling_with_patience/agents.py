# can choose to just import mesa or to do these and streamline code a little
from mesa import Agent
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector


# set up and initialize the agents
class SegAgent(Agent):
    def __init__(self, pos, model, agent_type, intolerance = 0.375, patience=0.5):  # agents and their characteristics
        super().__init__(pos, model)
        # constants
        self.pos = pos
        self.type = agent_type
        self.patience = patience
        self.intolerance = intolerance
        

        # variables
        self.neighbors_a = 0  # count of neighbors for each agent (ignore empty squares)
        self.a_pct_similar = 0  # calculate neighbor percents
        self.impatience = 0 # the patience level of the agent. If patience >= 1, the agent moves
        self.similar = 0  # agent-specific measures of neighbor similarity
        self.similar0 = 0
        self.similar1 = 0
        self.is_happy = False

        

    # describe what happens in each step for the agents
    # agents check surroundings and count neighbors of the same type
    def step(self):
        self.similar = 0  # reset these counters each time step
        self.similar0 = 0
        self.similar1 = 0
        self.neighbors_a = 0
        self.a_pct_similar = 0

        # get neighbors and determine if your intolerance threshold is met
        for neighbor in self.model.grid.iter_neighbors(self.pos, True):
            self.neighbors_a += 1

            if neighbor.type == self.type:
                self.similar += 1

                if self.type == 0:
                    self.similar0 += 1

                elif self.type == 1:
                    self.similar1 += 1

        # If unhappy, increase patience:
        # this permits different types to have different group thresholds
        if self.similar < 8 * self.intolerance:
            self.impatience += 0.1
            self.impatience = min(self.impatience, self.patience)
            self.is_happy = False
            if self.impatience >= self.patience:
                self.move()
        else:
            self.impatience -= 0.1
            self.impatience = max(0, self.patience)
            self.is_happy = True

        if self.neighbors_a > 0:
            self.a_pct_similar = round(100 * self.similar / self.neighbors_a, 1)
        else:
            self.a_pct_similar = 0

    # set up the actions available to agents
    def move(self):
        neighborhood = self.model.grid.get_neighborhood(
            self.pos,
            moore=False,
            include_center=False
        )
        possible_steps = [self.pos]
        for xy in neighborhood:
            if self.model.grid.is_cell_empty(xy):
                possible_steps += [xy]
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

