

import itertools

import mesa
import numpy as np
import pandas as pd
import random

# parameter lists for each parameter to be tested in batch run
def run(save_to):
    br_params = {"step_by_type": True,
                 "grass": True,
                 "grass_regrowth_time" : 20,
                 "initial_sheep" : 150,
                 "initial_wolves" : 20
                 }
    
    if __name__ == "__main__":
        data = mesa.batch_run(
            WolfSheep,
            br_params,
            max_steps = 100,
            data_collection_period = 1, 
            iterations = 1
        )
        br_df = pd.DataFrame(data)
        br_df.to_csv(save_to)


# batch_run with original model
from wolf_sheep_original.model import WolfSheep
run(save_to = "data/original_single.csv")

# batch_run with intelligent model
from wolf_sheep.model import WolfSheep
run(save_to = "data/updated_single.csv")
