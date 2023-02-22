import itertools

import mesa
import numpy as np
import pandas as pd

from bank_reserves.agents import Bank, Person
from bank_reserves.model import BankReserves

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
        BankReserves,
        br_params,
        max_steps = 100,
        data_collection_period = 10,
        iterations = 50
    )
    br_df = pd.DataFrame(data)
    br_df.to_csv("data/data.csv")
