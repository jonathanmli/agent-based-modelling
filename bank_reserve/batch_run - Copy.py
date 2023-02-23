import itertools

import mesa
import numpy as np
import pandas as pd

from bank_reserves.agents import Bank, Person

# Start of datacollector functions


def get_num_rich_agents(model):
    """list of rich agents"""

    rich_agents = [a for a in model.schedule.agents if a.savings > model.rich_threshold]
    # return number of rich agents
    return len(rich_agents)


def get_num_poor_agents(model):
    """list of poor agents"""

    poor_agents = [a for a in model.schedule.agents if a.loans > 10]
    # return number of poor agents
    return len(poor_agents)


def get_num_mid_agents(model):
    """list of middle class agents"""

    mid_agents = [
        a
        for a in model.schedule.agents
        if a.loans < 10 and a.savings < model.rich_threshold
    ]
    # return number of middle class agents
    return len(mid_agents)


def get_total_savings(model):
    """list of amounts of all agents' savings"""

    agent_savings = [a.savings for a in model.schedule.agents]
    # return the sum of agents' savings
    return np.sum(agent_savings)


def get_total_wallets(model):
    """list of amounts of all agents' wallets"""

    agent_wallets = [a.wallet for a in model.schedule.agents]
    # return the sum of all agents' wallets
    return np.sum(agent_wallets)


def get_total_money(model):
    """sum of all agents' wallets"""

    wallet_money = get_total_wallets(model)
    # sum of all agents' savings
    savings_money = get_total_savings(model)
    # return sum of agents' wallets and savings for total money
    return wallet_money + savings_money


def get_total_loans(model):
    """list of amounts of all agents' loans"""

    agent_loans = [a.loans for a in model.schedule.agents]
    # return sum of all agents' loans
    return np.sum(agent_loans)


def track_params(model):
    return (model.init_people, model.rich_threshold, model.reserve_percent)


def track_run(model):
    return model.uid


class BankReservesModel(mesa.Model):
    # id generator to track run number in batch run data
    id_gen = itertools.count(1)

    # grid height
    grid_h = 20
    # grid width
    grid_w = 20

    """init parameters "init_people", "rich_threshold", and "reserve_percent"
       are all set via Slider"""

    def __init__(
        self,
        height=grid_h,
        width=grid_w,
        init_people=2,
        rich_threshold=10,
        reserve_percent=50,
        deposit_interest=1,
        loan_interest=2,
        risk_mu = 5,
        risk_sigma = 5,
        risk_preference = 0.5
    ):
        self.uid = next(self.id_gen)
        self.height = height
        self.width = width
        self.init_people = init_people
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=True)
        # rich_threshold is the amount of savings a person needs to be considered "rich"
        self.rich_threshold = rich_threshold
        self.reserve_percent = reserve_percent
        self.deposit_interest = deposit_interest
        self.loan_interest = loan_interest
        
        # set risk asset profit and variance
        self.risk_mu = risk_mu
        self.risk_sigma = risk_sigma
        
        # set risk preference
        self.risk_preference = risk_preference
        
        # see datacollector functions above
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Rich": get_num_rich_agents,
                "Poor": get_num_poor_agents,
                "Middle Class": get_num_mid_agents,
                "Savings": get_total_savings,
                "Wallets": get_total_wallets,
                "Money": get_total_money,
                "Loans": get_total_loans,
                "Model Params": track_params,
                "Run": track_run,
            },
            agent_reporters={"Wealth": "wealth"},
        )

        # create a single bank for the model
        self.bank = Bank(1, self, self.reserve_percent, 
                         self.deposit_interest, self.loan_interest, self.risk_preference)

        # create people for the model according to number of people set by user
        for i in range(self.init_people):
            # set x coordinate as a random number within the width of the grid
            x = self.random.randrange(self.width)
            # set y coordinate as a random number within the height of the grid
            y = self.random.randrange(self.height)
            p = Person(i, (x, y), self, True, self.bank, self.rich_threshold)
            # place the Person object on the grid at coordinates (x, y)
            self.grid.place_agent(p, (x, y))
            # add the Person object to the model schedule
            self.schedule.add(p)

        self.running = True

    def step(self):
        # collect data
        self.datacollector.collect(self)
        # bank deside the amount of the risk asset
        self.bank.invest_risky_asset()
        # tell all the agents in the model to run their step function
        self.schedule.step()
        # bank get investment profit/loss after persons step
        self.bank.get_result_from_investment()

    def run_model(self):
        for i in range(self.run_time):
            self.step()

# parameter lists for each parameter to be tested in batch run
br_params = {
    "init_people": [100],
    "rich_threshold": [10],
    "reserve_percent": [10, 20, 30],
    "loan_interest": [1, 2, 3],
    "risk_mu": [3, 5, 7],
    "risk_sigma": [5]
}

if __name__ == "__main__":
    data = mesa.batch_run(
        BankReservesModel,
        br_params,
        max_steps = 100,
        data_collection_period = 10,
        iterations = 50
    )
    br_df = pd.DataFrame(data)
    br_df.to_csv("data/data.csv")
