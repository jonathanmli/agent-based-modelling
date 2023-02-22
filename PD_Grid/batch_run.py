import mesa
import numpy as np
import pandas as pd
import random

from pd_grid.model import PdGrid

# parameter lists for each parameter to be tested in batch run
br_params = {
    "schedule_type": ["Random", "Sequential", "Simultaneous"],
    "seed": list(range(1,51)),
    "payoff_type": ['pd', 'sh']
}

if __name__ == "__main__":
    data = mesa.batch_run(
        PdGrid,
        br_params,
        max_steps = 100,
        data_collection_period = 1,
        iterations = 1,
	  number_processes = 4
    )
    br_df = pd.DataFrame(data)
    br_df.to_csv("data/PD_grid.csv")