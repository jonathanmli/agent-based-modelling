# libraries
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
sns.set_style("darkgrid")

# get buatch run data
df = pd.read_csv('data/PD_grid.csv') # original model
df = df[df['payoff_type'] == 'sh']

# modefy 
df = df[['RunId', 'Step', 'schedule_type', 'Avg_Weight0', 'Ct_Weight0 > 0.5']]
df.rename({'Ct_Weight0 > 0.5': 'Cooperating_Agents'}, axis=1, inplace=True)
df['model'] = 'updated'

# get data of original model for comparision
df_original = pd.read_csv('data/PD_grid_original.csv')
df_original = df_original[['RunId', 'Step', 'schedule_type','Cooperating_Agents']]
df_original['model'] = 'original'

# combine
df = pd.concat([df, df_original])

## 1.1 the effect of schedule type-------------------------------------------

# get subset df
df_random = df[df['schedule_type']=='Random']
df_sequential = df[df['schedule_type']=='Sequential']
df_simultaneous = df[df['schedule_type']=='Simultaneous']

# get group df average and std of each model/activation tipe
df_g = df.groupby(['Step','model','schedule_type'], as_index=False)['Cooperating_Agents'].mean()
df_g_std = df.groupby(['Step','model','schedule_type'], as_index=False)['Cooperating_Agents'].std()
df_g['std'] = df_g_std['Cooperating_Agents']

# plot  --------------------------------------------------------------
fig, ax = plt.subplots(3, 1, figsize=(8,12), sharex=True, sharey = True)

# color palette as dictionary
palette = {"updated":"tab:purple",
           "original":"tab:orange"}

def scatter_plot(df, ax_num):
    sns.scatterplot(df, x='Step', y='Cooperating_Agents',
                    hue='model', alpha=0.1, sizes = 0.2,
                    palette = palette, ax=ax[ax_num]
                    )
def line_plot(activation, ax_num):
    sns.lineplot(df_g[df_g['schedule_type']==activation],
                 x='Step', y='Cooperating_Agents',
                 hue='model', palette = palette, linewidth =2, ax=ax[ax_num]
                 )

# ax0
scatter_plot(df_random, 0)
line_plot('Random', 0)
ax[0].set_title('Schedule_type = Random')

# ax1
scatter_plot(df_sequential, 1)
line_plot('Sequential', 1)
ax[1].set_title('Schedule_type = Sequential')

# ax2
scatter_plot(df_simultaneous, 2)
line_plot('Simultaneous', 2)
ax[2].set_title('Schedule_type = Simultaneous')

# set title
fig.suptitle('Number of cooprating agents', fontsize=18)
plt.savefig('figure/num_of_coop.png')



