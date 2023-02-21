import mesa
import random
import numpy as np

from .agent import PDAgent


class PdGrid(mesa.Model):
    """Model class for iterated, spatial prisoner's dilemma model."""
    
    schedule_types = {
        "Sequential": mesa.time.BaseScheduler,
        "Random": mesa.time.RandomActivation,
        "Simultaneous": mesa.time.SimultaneousActivation,
    }

    # This dictionary holds the payoff for this agent,
    # keyed on: (my_move, other_move)
    payoff_types = {
        "pd": {("C", "C"): 2, ("C", "D"): 0, ("D", "C"): 3, ("D", "D"): 1},
        'sh': {("C", "C"): 3, ("C", "D"): 0, ("D", "C"): 2, ("D", "D"): 1}
    }

    def __init__(
        self, width=50, height=50, schedule_type="Random", payoffs=None, seed=10, payoff_type='pd'
    ):

        """/
        Create a new Spatial Prisoners' Dilemma Model.

        Args:
            width, height: Grid size. There will be one agent per grid cell.
            schedule_type: Can be "Sequential", "Random", or "Simultaneous".
                           Determines the agent activation regime.
            payoffs: (optional) Dictionary of (move, neighbor_move) payoffs.
        """
        # allow random seed
        mesa.Model.reset_randomizer(self, seed) #comment this out -- helps for replicability
        random.seed(seed)        

        self.grid = mesa.space.SingleGrid(width, height, torus=True)
        self.schedule_type = schedule_type
        self.schedule = self.schedule_types[self.schedule_type](self)
        self.payoff_type = payoff_type
        self.payoff = self.payoff_types[self.payoff_type]
        
        
    
        # Create agents
        for x in range(width):
            for y in range(height):
                agent = PDAgent((x, y), self)
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)

        self.datacollector = mesa.DataCollector(
            {
                "Cooperating_Agents": lambda m: len([a for a in m.schedule.agents if a.move == "C"]),
                "Avg_Weight0": lambda m: np.mean([a.action0Weight for a in m.schedule.agents]),
                "Ct_Weight0 > 0.5": lambda m: len([a for a in m.schedule.agents if a.action0Weight > 0.5])
            }
        )

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

    def run(self, n):
        """Run the model for n steps."""
        for _ in range(n):
            self.step()
