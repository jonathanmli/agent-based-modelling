

import itertools

import mesa
import numpy as np
import pandas as pd
import random

# parameter lists for each parameter to be tested in batch run
def run(save_to):
    br_params = {"step_by_type": [False, True],
                 "grass": True,
                 "grass_regrowth_time" : [5, 20, 35],
                 "initial_sheep" : [100, 150, 200],
                 "initial_wolves" : [10, 20, 30]
                 }
    
    if __name__ == "__main__":
        data = mesa.batch_run(
            WolfSheep,
            br_params,
            max_steps = 100,
            data_collection_period = 2, # to reduce the datasize
            iterations = 50
        )
        br_df = pd.DataFrame(data)
        br_df.to_csv(save_to)


# batch_run with original model
from wolf_sheep_original.model import WolfSheep
run(save_to = "data/original.csv")

# batch_run with intelligent model
from wolf_sheep.model import WolfSheep
run(save_to = "data/updated.csv")

