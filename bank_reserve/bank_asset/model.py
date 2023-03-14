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

from bank_asset.agents import Bank, Firm

"""
If you want to perform a parameter sweep, call batch_run.py instead of run.py.
For details see batch_run.py in the same directory as run.py.
"""

# Start of datacollector functions


def get_num_big_agents(model):
    """return number of rich agents"""
    rich_agents = [a for a in model.schedule.agents if a.is_big()]
    return len(rich_agents)

def get_num_op_agents(model):
    """return number of rich agents"""
    rich_agents = [a for a in model.schedule.agents if a.is_operating()]
    return len(rich_agents)

def get_num_n_op_agents(model):
    """return number of rich agents"""
    rich_agents = [a for a in model.schedule.agents if a.is_not_operating()]
    return len(rich_agents)

def get_num_bankrupt_agents(model):
    """return number of rich agents"""
    rich_agents = [a for a in model.schedule.agents if a.is_bankrupt()]
    return len(rich_agents)

def get_num_non_big_agents(model):
    """return number of rich agents"""
    rich_agents = [a for a in model.schedule.agents if a.is_not_big()]
    return len(rich_agents)

def get_num_poor_agents(model):
    """return number of poor agents"""
    poor_agents = [a for a in model.schedule.agents if a.is_small()]
    return len(poor_agents)

def get_num_mid_agents(model):
    """return number of middle class agents"""
    mid_agents = [a for a in model.schedule.agents if a.is_medium()]
    return len(mid_agents)

def get_l_crisis(model):
    return model.bank.l_crisis

def get_total_savings(model):
    """sum of all agents' savings"""
    agent_savings = [a.savings for a in model.schedule.agents]
    # return the sum of agents' savings
    return float(np.sum(agent_savings))

def get_number_transactions(model):
    return len(model.p_history)

def get_total_cash(model):
    """sum of amounts of all cash in economy"""
    agent_cash = [a.cash for a in model.schedule.agents]
    # return the sum of all agents' wallets
    return float(np.sum(agent_cash))

def get_total_valuation(model):
    # sum of all agents' valuations
    firm_valuation = [a.valuation() for a in model.schedule.agents]
    return np.sum(firm_valuation)

def get_total_assets(model):
    agent_asset0s = [a.asset0 for a in model.schedule.agents]
    return float(np.sum(agent_asset0s))

def get_total_loans(model):
    # list of amounts of all agents' loans
    agent_loans = [a.loans for a in model.schedule.agents]
    # return sum of all agents' loans
    return float(np.sum(agent_loans))

def get_avg_p_asset0(model):
    return model.p_asset0

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
        poor_threshold = 5,
        reserve_percent=50,
        deposit_interest=1,
        loan_interest=2,
        risk_mu = 5,
        risk_sigma = 5,
        risk_preference = 0.5,
        p_asset0 = 10,
        fed_interest = 2,
        eta = 0.5,
        birthrate = 0.1
    ):
        self.height = height
        self.width = width
        self.init_people = init_people
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=True)
        # rich_threshold is the amount of savings a person needs to be considered "rich"
        self.rich_threshold = rich_threshold
        self.poor_threshold = poor_threshold
        self.reserve_percent = reserve_percent
        self.deposit_interest = deposit_interest
        self.loan_interest = loan_interest
        self.p_asset0 = p_asset0
        self.fed_interest = fed_interest
        self.p_history = []
        self.eta = eta
        self.birthrate = birthrate
        self.current_id = 0
        
        
        # set risk asset profit and variance
        self.risk_mu = risk_mu
        self.risk_sigma = risk_sigma
        
        # set risk preference
        self.risk_preference = risk_preference
        
        # see datacollector functions above
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Big": get_num_big_agents,
                "Bankrupt": get_num_bankrupt_agents,
                "Small": get_num_non_big_agents,
                "Total Savings": get_total_savings,
                "Total Valuation": get_total_valuation,
                "Total Assets": get_total_assets,
                "Total Loans": get_total_loans,
                "Average Price of Asset": get_avg_p_asset0,
                "Total Bank Liquidity Crisis": get_l_crisis,
                "Number of Transactions": get_number_transactions,
                "Total Cash": get_total_cash,
                "Operating": get_num_op_agents,
                "Not Operating": get_num_n_op_agents,
            },
            agent_reporters={"Valuation": lambda x: x.valuation()},
        )

        # create a single bank for the model
        self.bank = Bank(1, self, self.reserve_percent, 
                         self.deposit_interest, self.loan_interest, self.risk_preference)

        # create people for the model according to number of people set by user
        for i in range(self.init_people):
            self.create_firm(self.bank)

        self.running = True
        self.datacollector.collect(self)
        

    def create_firm(self, bank, **kwargs):
        # set x, y coords randomly within the grid
        x = self.random.randrange(self.width)
        y = self.random.randrange(self.height)
        p = Firm(self.next_id(), (x, y), self, True, bank, **kwargs)
        # place the Person object on the grid at coordinates (x, y)
        self.grid.place_agent(p, (x, y))
        # add the Person object to the model schedule
        self.schedule.add(p)

    def adjust_p_asset0(self):
        if len(self.p_history) > 0:
            self.p_asset0  +=  self.eta * np.average(self.p_history)- (1-self.eta) * self.p_asset0
            self.p_history = []
        
    def report_p_asset0(self, p):
        self.p_history += [p]
        print('traded')

    def firm_birth(self):
        if self.random.uniform(0,1) < self.birthrate:
            self.create_firm(self.bank)
            print("birth")

    def step(self):
        # bank adjust interest rates
        self.bank.adjust_rates()
        # tell all the agents in the model to run their step function
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)
        # adjust average p_asset0 prices
        self.adjust_p_asset0()
        # create new firms
        self.firm_birth()

    def run_model(self):
        for i in range(self.run_time):
            self.step()