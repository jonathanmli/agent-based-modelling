# libraries
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os
import gc
sns.set_style("darkgrid")

# get buatch run data
df_original = pd.read_csv('data/original.csv') # original model
df_updated = pd.read_csv('data/updated.csv') # intelligent model

df_original['agent_type'] = 'original'
df_updated['agent_type'] = 'updated'

# merge two dataset
df = pd.concat([df_original, df_updated], axis=0)

# delete two df for save memory
del [[df_original, df_updated]]
gc.collect()

# plotting
agents = ['Sheep', 'Wolves', 'Grass']

def group_plot(by ,var):
    df_mean = df.groupby([by,'Step']).mean().reset_index()
    sns.lineplot(df_mean, x = 'Step', y = var, hue = by)


# 1.evaluation of the modification we made in assignment2 ----------------------
## 1.1 the activaion is matter?

# quick check, activation does not matter
for v in agents:
    group_plot(by='step_by_type', var = v)
    plt.savefig(f'plots/step_by_type_{v}.png')
    plt.close()

## 1.2 the rule change is matter?
#  changing agent rule has some impact on the pass
for v in agents:
    group_plot(by='agent_type', var = v)
    plt.savefig(f'plots/agent_type_{v}.png')
    plt.close()

# 2. vary the initial setting -----------------------------
# vary the density and relative population of wolf and sheep
df_10step = df[df['Step'] == 10]

## 2.1 the distribution of the wolf after 10 steps
g = sns.FacetGrid(df_10step, row="initial_sheep",
                  col="initial_wolves",
                  hue='agent_type',
                  height= 1.8,
                  aspect=1.4,
                  margin_titles=True,
                  palette = 'Set2'
                  )
g.add_legend()
g.map(sns.kdeplot, "Wolves")
plt.savefig('plots/distribution_wolves')
# it is similar even though we change the agent behaviour
# initial population of sheep does not have impact
# initial population of wolves have impact


## 2.2 the distribution of the sheep after 10 steps
g = sns.FacetGrid(df_10step, row="initial_sheep",
                  col="initial_wolves",
                  hue='agent_type',
                  height= 1.8,
                  aspect=1.4,
                  margin_titles=True,
                  palette = 'Set2'
                  )
g.add_legend()
g.map(sns.kdeplot, "Sheep")
plt.savefig('plots/distribution_Sheep')
# the rule change affects significantly on sheeps population
# if there are more wolves, sheep tend to extinct early
# the initial number of sheep does not matter


# how the climate shock affect the path of each agent ----------------------------------
# choose base line case
temp = df[(df['agent_type'] == 'updated')& # use intelligent model
          (df['step_by_type'] == True)&
           (df['initial_sheep'] == 150)&
           (df['initial_wolves'] == 20)
           ]

# choose extreme climate case
temp = temp[(temp['grass_regrowth_time'] == 5) | (temp['grass_regrowth_time'] == 35)]

# the wolfe paths are different
sns.lmplot(data=temp, x='Step', y='Wolves', hue = 'grass_regrowth_time',
           palette = 'Set1',
           legend_out = False,
           order=4,
           scatter_kws={"s": 10, 'alpha':0.2})
plt.savefig('plots/climate_effect_wolves')

# the sheep paths are similar
sns.lmplot(data=temp, x='Step', y='Sheep', hue = 'grass_regrowth_time',
           palette = 'Set1',
           legend_out = False,
           order=4,
           scatter_kws={"s": 10, 'alpha':0.2})
plt.savefig('plots/climate_effect_Sheep')

# the Grass path
sns.lmplot(data=temp, x='Step', y='Grass', hue = 'grass_regrowth_time',
           palette = 'Set1',
           legend_out = False,
           order=4,
           scatter_kws={"s": 10, 'alpha':0.2})
plt.savefig('plots/climate_effect_Grass')

# wolf paths are more likely to be affected by the climate change. it is interesting result
