# Schelling Segregation Model -- Three type of agents --
**Main text taken from Mesa Examples Library

## Summary

We added a third type of agent to the basic Schelling Segregation model. This change allows us to analyze more realistic settings because there are some -- not two -- types of people in the actual city.

## What we do

First, we define three groups, ``Majority(GroupA)``, ``Minority1(GroupB)``, ``Minority1(GroupB)``. To mesure happiness and related variables of all three types, we also added some initial variables in ``model.py`` and ``agents.py``. 

Then, we also tweaked ``server`` side. To define the ratio of all three type of people, we added an extra user settable parameter. Due to this change, users can change the ratio of majority, minority1, and minority2 as they wish. 

## Installation

To install the dependencies use pip and the requirements.txt in this directory. e.g.

```
    $ pip install -r requirements.txt
```

## How to Run

To run the model interactively, run ``mesa runserver`` in this directory. e.g.

```
    $ mesa runserver
```

Then open your browser to [http://127.0.0.1:8521/](http://127.0.0.1:8521/) and press Reset, then Run.

To view and run some example model analyses, launch the IPython Notebook and open ``analysis.ipynb``. Visualizing the analysis also requires [matplotlib](http://matplotlib.org/).

## How to Run without the GUI

To run the model with the grid displayed as an ASCII text, run `python run_ascii.py` in this directory.

## Files

* ``run.py``: Launches a model visualization server.
* ``run_ascii.py``: Run the model in text mode.
* ``schelling.py``: Contains the agent class, and the overall model class.
* ``server.py``: Defines classes for visualizing the model in the browser via Mesa's modular server, and instantiates a visualization server.
