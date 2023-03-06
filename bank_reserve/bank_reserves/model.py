"""
The following code was adapted from the Bank Reserves model included in Netlogo
Model information can be found at: http://ccl.northwestern.edu/netlogo/models/BankReserves
Accessed on: November 2, 2017
Author of NetLogo code:
    Wilensky, U. (1998). NetLogo Bank Reserves model.
    http://ccl.northwestern.edu/netlogo/models/BankReserves.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
"""

import mesa
import numpy as np
from scipy import stats

from bank_reserves.agents import Bank, Person

"""
If you want to perform a parameter sweep, call batch_run.py instead of run.py.
For details see batch_run.py in the same directory as run.py.
"""

# Start of datacollector functions


def get_num_rich_agents(model):
    """return number of rich agents"""

    rich_agents = [a for a in model.schedule.agents if a.savings > model.rich_threshold]
    return len(rich_agents)


def get_num_poor_agents(model):
    """return number of poor agents"""

    poor_agents = [a for a in model.schedule.agents if a.loans > 10]
    return len(poor_agents)


def get_num_mid_agents(model):
    """return number of middle class agents"""

    mid_agents = [
        a
        for a in model.schedule.agents
        if a.loans < 10 and a.savings < model.rich_threshold
    ]
    return len(mid_agents)


def get_total_savings(model):
    """sum of all agents' savings"""

    agent_savings = [a.savings for a in model.schedule.agents]
    # return the sum of agents' savings
    return np.sum(agent_savings)


def get_total_wallets(model):
    """sum of amounts of all agents' wallets"""

    agent_wallets = [a.wallet for a in model.schedule.agents]
    # return the sum of all agents' wallets
    return np.sum(agent_wallets)


def get_total_money(model):
    # sum of all agents' wallets
    wallet_money = get_total_wallets(model)
    # sum of all agents' savings
    savings_money = get_total_savings(model)
    # return sum of agents' wallets and savings for total money
    return wallet_money + savings_money


def get_total_loans(model):
    # list of amounts of all agents' loans
    agent_loans = [a.loans for a in model.schedule.agents]
    # return sum of all agents' loans
    return np.sum(agent_loans)

def gini_coefficient(model):
    # get agent wealth
    agent_wealth = [a.wealth for a in model.schedule.agents]
    # convert the list to a numpy array
    x = np.array(agent_wealth)
    if max(x) == 0:
        gini_coef = 0
    else:
        x_min = min(x)
        x = x - x_min
        # sort the array in ascending order
        sorted_x = np.sort(x)
        # calculate cumulative sum
        cumx = np.cumsum(sorted_x)
        # calculate the Lorenz curve values
        Lorenz_curve = cumx / cumx[-1]
        # calculate the Gini coefficient using the area formula
        gini_coef = 1 - 2 * np.trapz(Lorenz_curve, np.linspace(0, 1, len(x)))
    return gini_coef

def gini_coefficient2(model):
    # get agent wealth
    agent_saving = [a.savings for a in model.schedule.agents]
    # convert the list to a numpy array
    x = np.array(agent_saving)
    if max(x) == 0:
        gini_coef = 0
    else:
        x_min = min(x)
        x = x - x_min
        # sort the array in ascending order
        sorted_x = np.sort(x)
        # calculate cumulative sum
        cumx = np.cumsum(sorted_x)
        # calculate the Lorenz curve values
        Lorenz_curve = cumx / cumx[-1]
        # calculate the Gini coefficient using the area formula
        gini_coef = 1 - 2 * np.trapz(Lorenz_curve, np.linspace(0, 1, len(x)))
    return gini_coef


class BankReserves(mesa.Model):
    """
    This model is a Mesa implementation of the Bank Reserves model from NetLogo.
    It is a highly abstracted, simplified model of an economy, with only one
    type of agent and a single bank representing all banks in an economy. People
    (represented by circles) move randomly within the grid. If two or more people
    are on the same grid location, there is a 50% chance that they will trade with
    each other. If they trade, there is an equal chance of giving the other agent
    $5 or $2. A positive trade balance will be deposited in the bank as savings.
    If trading results in a negative balance, the agent will try to withdraw from
    its savings to cover the balance. If it does not have enough savings to cover
    the negative balance, it will take out a loan from the bank to cover the
    difference. The bank is required to keep a certain percentage of deposits as
    reserves and the bank's ability to loan at any given time is a function of
    the amount of deposits, its reserves, and its current total outstanding loan
    amount.
    """

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
                "gini": gini_coefficient,
                "gini2": gini_coefficient2,
            },
            agent_reporters={"Wealth": lambda x: x.wealth},
        )

        # create a single bank for the model
        self.bank = Bank(1, self, self.reserve_percent, 
                         self.deposit_interest, self.loan_interest, self.risk_preference)

        # create people for the model according to number of people set by user
        for i in range(self.init_people):
            # set x, y coords randomly within the grid
            x = self.random.randrange(self.width)
            y = self.random.randrange(self.height)
            p = Person(i, (x, y), self, True, self.bank, self.rich_threshold)
            # place the Person object on the grid at coordinates (x, y)
            self.grid.place_agent(p, (x, y))
            # add the Person object to the model schedule
            self.schedule.add(p)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        # bank deside the amount of the risk asset
        self.bank.invest_risky_asset()
        # tell all the agents in the model to run their step function
        self.schedule.step()
        # bank get investment profit/loss after persons step
        self.bank.get_result_from_investment()
        # collect data
        self.datacollector.collect(self)

    def run_model(self):
        for i in range(self.run_time):
            self.step()