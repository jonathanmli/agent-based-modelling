# Assignment1: additional parameters to the Schelling segregation model

Shogo Nakano / Jonathan Li
(507 words)

**Main text taken from Mesa Examples Library

## Background and summary of change

The base model is the Schelling segregation model, which shows how even a mild preference for similar neighbors can lead to a much higher degree of segregation than we would intuitively expect. However, since the original model was based on several unrealistic assumptions, we attempted to improve it in several ways. The changes are (1) adding patience, (2) changing how agents move (restricting the ability to move), and (3) heterogeneity of agent tolerance.

## Design concepts

The basic design concepts are the same as the original model. In other words:

**Who**: There are two types of agents. Majority and Minority.  The population ratio is user settable parameter.

**Does what**: Each agent calculates whether the percentage of the different types of agents among his neighbor exceeds his tolerance. If it exceeds, the patience increases; if not, it decreases. Agents that exceed a certain tolerance level are moved to another cell. He can only move their surrounding cells in one step.

**How**: Agents on a 16*16 grid interact with one another in each step. We use random initialization, and all agents act simultaneously in each step. The agents have their own tolerance and patience levels, which follow the beta distribution.


## Details

This section will focus on what we changed from the original model, and other points will be briefly discussed.

First, we added patience. In the original model, unhappy agents were immediately moved to another available cell. In reality, however, agents are expected to move with some lag for various reasons, including the cost of moving and the time required to conduct a new house search (Information asymmetry may make it take longer to find a home). This parameter eliminates the immediate move by the unhappy agent.

Second, we changed how agents move. In the original model, agents can move anywhere, no matter how far the new cell is. However, this assumption is also unrealistic because it fails to take into account the cost of moving. Therefore, we restrict the cells where the agents can move. Precisely, it can move to only 8 cells around itself. The agents must be moved further if the move does not improve their situation. However, they will no longer have to move unlimitedly around in all directions in the grid.

Lastly, we change the initialization method of intolerance.  Although the original model assumed that all agents had identical intolerance, it is natural to assume that there is heterogeneity in these preferences. Therefore, we assumed that intolerance follows a beta distribution, allowing for agents’ heterogeneity. We also use the same method for the initialization of patience. The mean of the distribution is a user settable parameter.

These changes are intended to relax the previous model's overly strong assumptions and make the model more complex. In particular, the first two changes restrict the agent's ability to move and the speed of his decision to move. By varying these constraints (like moving ability or patience) and observing how the behavior of the model changes, we expect to get an indication of how cost constraints or information collection capacity issues affect segregation.


-------------------------

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
* ``analysis.ipynb``: Notebook demonstrating how to run experiments and parameter sweeps on the model.

## Further Reading

Schelling's original paper describing the model:

[Schelling, Thomas C. Dynamic Models of Segregation. Journal of Mathematical Sociology. 1971, Vol. 1, pp 143-186.](https://www.stat.berkeley.edu/~aldous/157/Papers/Schelling_Seg_Models.pdf)

An interactive, browser-based explanation and implementation:

[Parable of the Polygons](http://ncase.me/polygons/), by Vi Hart and Nicky Case.
