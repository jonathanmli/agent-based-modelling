from model import PdGrid
from mesa.batchrunner import FixedBatchRunner
import json

import numpy as np
import pandas as pd

# parameters that will remain constant
fixed_parameters = {
    'width':50,
   'height':50,
   'payoffs':None,
   'schedule_type':'Random'
}

# parameters you want to vary
# can also include combinations here
# parameters_list = [{'schedule_type':'Sequential'},{ 'schedule_type':'Random'},{ 'schedule_type':'Simultaneous'}]
parameters_list = {'seed': range(10)}


# what to run and what to collect
# iterations is how many runs per parameter value
# max_steps is how long to run the model
max_steps,iterations = 2, 1
batch_run = FixedBatchRunner(PdGrid, parameters_list,
                             fixed_parameters, iterations=iterations,
                             model_reporters={"Ct Cooperating": lambda m: len([a for a in m.schedule.agents if a.move == "C"])},
                             max_steps=max_steps)

# run the batches of your model with the specified variations
batch_run.run_all()


## NOTE: to do data collection, you need to be sure your pathway is correct to save this!
# Data collection
# extract data as a pandas Data Frame
batch_dict = batch_run.get_collector_model()
batch_save = {f'{key[0]}_{key[1]}':list(value['Cooperating_Agents']) for key,value in batch_dict.items()}
json.dump(batch_save, open("../batch_list.json", 'w'), indent = 4)
