import mesa

from bank_asset.agents import Firm
from bank_asset.model import BankReserves

"""
Citation:
The following code was adapted from server.py at
https://github.com/projectmesa/mesa/blob/main/examples/wolf_sheep/wolf_sheep/server.py
Accessed on: November 2, 2017
Author of original code: Taylor Mutch
"""

# The colors here are taken from Matplotlib's tab10 palette
# Green
BIG_COLOR = "#2ca02c"
# Red
BANKRUPT_COLOR = "#d62728"
# Blue
SMALL_COLOR = "#1f77b4"
# Black
TEXT_COLOR = "#000000"


def person_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    # update portrayal characteristics for each Person object
    if isinstance(agent, Firm):
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.5
        portrayal["Layer"] = 0
        portrayal["Filled"] = "true"
        portrayal["text"] = int(agent.valuation())
        portrayal["text_color"] = TEXT_COLOR

        color = SMALL_COLOR

        # set agent color based on savings and loans
        if agent.valuation() < 0:
            color = BANKRUPT_COLOR
        elif agent.is_big():
            color = BIG_COLOR
        else:
            color = SMALL_COLOR
        
        portrayal["Color"] = color

    return portrayal


# dictionary of user settable parameters - these map to the model __init__ parameters
model_params = {
    "init_people": mesa.visualization.Slider(
        "People", 25, 1, 200, description="Initial Number of People"
    ),
    "rich_threshold": mesa.visualization.Slider(
        "Rich Threshold",
        10,
        1,
        20,
        description="Upper End of Random Initial Wallet Amount",
    ),
    "reserve_percent": mesa.visualization.Slider(
        "Reserves",
        50,
        1,
        100,
        description="Percent of deposits the bank has to hold in reserve",
    ),
    "deposit_interest": mesa.visualization.Slider(
        "deposit_interest",
        0.1,
        0,
        1,
        0.1,
        description="the interest rate of deposit",
    ),
    "loan_interest": mesa.visualization.Slider(
        "loan_interest",
        1,
        0,
        10,
        description="the interest rate of loan",
    ),
    "risk_mu": mesa.visualization.Slider(
        "risk_mu",
        3,
        0,
        10,
        description="the average profit of risk asset",
    ),
    "risk_sigma": mesa.visualization.Slider(
        "risk_sigma",
        3,
        0,
        10,
        description="the standard deviation of risk asset profit",
    ),
    "risk_preference": mesa.visualization.Slider(
        "risk_preference",
        0.5,
        0,
        1,
        0.1,
        description="the risk preference of the bank",
    ),
}

# set the portrayal function and size of the canvas for visualization
canvas_element = mesa.visualization.CanvasGrid(person_portrayal, 20, 20, 500, 500)

# map data to chart in the ChartModule
chart_element = mesa.visualization.ChartModule(
    [
        {"Label": "Big", "Color": BIG_COLOR},
        {"Label": "Bankrupt", "Color": BANKRUPT_COLOR},
        {"Label": "Small", "Color": SMALL_COLOR},
    ]
)

# create instance of Mesa ModularServer
server = mesa.visualization.ModularServer(
    BankReserves,
    [canvas_element, chart_element],
    "Bank Reserves Model",
    model_params=model_params,
)