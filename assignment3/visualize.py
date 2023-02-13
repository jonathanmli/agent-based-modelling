# libraries
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from PIL import Image
import os
import gc
sns.set_style("darkgrid")

# get single run data
df_original_single = pd.read_csv('data/original_single.csv') # original model
df_updated_single = pd.read_csv('data/updated_single.csv') # intelligent model

df_original_single['agent_type'] = 'original'
df_updated_single['agent_type'] = 'updated'

df_single = pd.concat([df_original_single, df_updated_single], axis=0)


# get buatch run data
df_original = pd.read_csv('data/original.csv') # original model
df_updated = pd.read_csv('data/updated.csv') # intelligent model

df_original['agent_type'] = 'original'
df_updated['agent_type'] = 'updated'

# merge two dataset
df = pd.concat([df_original, df_updated], axis=0)

# generate relative pop variable
df['relative_pop'] = df['initial_sheep'] / df['initial_wolves']

# categorize relative pop
def func_cate(x):
    if  x <= 5:
        return 'less_sheep'
    elif x > 5 and x <= 10:
        return 'moderate'
    elif x > 10 :
        return 'more_sheep'

df['relative_sheep'] = df['relative_pop'].apply(func_cate)


# delete two df for save memory
del [[df_original, df_updated]]
gc.collect()

# plotting
agents = ['Sheep', 'Wolves', 'Grass']

def group_plot(df, by ,var, i):
    df_mean = df.groupby([by,'Step']).mean().reset_index()
    sns.lineplot(df_mean, x = 'Step', y = var, hue = by, ax = axs[i])
    
# plot single run result -------------------------------------------------------
fig, axs = plt.subplots(1,3,figsize=(12,6))

for agent, i in zip(agents, range(0,3)):
    group_plot(df_single, by='agent_type', var = agent, i = i)
    
plt.savefig('plots/single.png')


# 1.evaluation of the modification we made in assignment2 ----------------------
## 1.1 the activaion is matter?

# quick check, activation does not matter
fig, axs = plt.subplots(1,3,figsize=(12,6))

for agent, i in zip(agents, range(0,3)):
    group_plot(df, by='step_by_type', var = agent, i = i)
    
plt.savefig('plots/step_by_type.png')

## 1.2 the rule change is matter?
#  changing agent rule has some impact on the pass
fig, axs = plt.subplots(1,3,figsize=(12,6))

for v, i  in zip(agents, range(0,3)):
    group_plot(df, by='agent_type', var = v, i = i)

plt.savefig('plots/agent_type.png')

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

## 2.3 check relative size effect

fig, axs = plt.subplots(1,2,figsize=(13,6))

df_10step = df[(df['Step'] == 10) &
               (df['agent_type'] == 'updated') &
               (df['initial_sheep'] == 150)
               ]
sns.kdeplot(df_10step, x='Sheep', hue='initial_wolves', palette= 'Set2', ax=axs[0])

df_10step = df[(df['Step'] == 10) &
               (df['agent_type'] == 'updated') &
               (df['initial_wolves'] == 20)
               ]

sns.kdeplot(df_10step, x='Wolves', hue='initial_sheep', palette= 'Set2', ax=axs[1])

axs[0].set(xlabel='Sheep (initial = 150)')
axs[1].set(xlabel='Wolves (initial = 20)')

plt.savefig('plots/distribution_fix.png')

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
           height=5,
           aspect=1.2,
           scatter_kws={"s": 10, 'alpha':0.2})
plt.savefig('plots/climate_effect_wolves.png')

# the sheep paths are similar
sns.lmplot(data=temp, x='Step', y='Sheep', hue = 'grass_regrowth_time',
           palette = 'Set1',
           legend_out = False,
           order=4,
           height=5,
           aspect=1.2,
           scatter_kws={"s": 10, 'alpha':0.2})
plt.savefig('plots/climate_effect_Sheep.png')

# the Grass path
sns.lmplot(data=temp, x='Step', y='Grass', hue = 'grass_regrowth_time',
           palette = 'Set1',
           legend_out = False,
           order=4,
           height=5,
           aspect=1.2,
           scatter_kws={"s": 10, 'alpha':0.2})
plt.savefig('plots/climate_effect_Grass.png')


# wolf paths are more likely to be affected by the climate change. it is interesting result

# combine png
def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

im1 = Image.open('plots/climate_effect_Sheep.png')
im2 = Image.open('plots/climate_effect_wolves.png')

get_concat_h(im1, im2).save('plots/climate_effect.png')

def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

im1 = Image.open('plots/distribution_Sheep.png')
im2 = Image.open('plots/distribution_wolves.png')

get_concat_v(im1, im2).save('plots/distribution.png')
