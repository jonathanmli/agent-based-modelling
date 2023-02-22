# libraries
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from PIL import Image
import os
import gc
sns.set_style("darkgrid")

# get buatch run data
df = pd.read_csv('data/data.csv') # original model

df.columns

"""
br_params = {
    "init_people": [100],
    "rich_threshold": [10],
    "reserve_percent": [10, 20, 30],
    "loan_interest": [1, 2, 3],
    "risk_mu": [3,5,7],
    "risk_sigma": [5]
}
"""

df.columns

## 1.1 the effect on aggregated data-------------------------------------------
# the effect on the average wealth
df_g = df.groupby(['Run','Step'])['loan_interest','reserve_percent','risk_mu',
                                  'Wealth','Rich','Poor','Middle Class'].mean().reset_index()

# total wealth path
# by changing loan_interest
sns.lineplot(df_g, x='Step', y='Wealth', hue='loan_interest')
# by changing reserve ratio
sns.lineplot(df_g, x='Step', y='Wealth', hue='reserve_percent')
# by changing risk_mu
sns.lineplot(df_g, x='Step', y='Wealth', hue='risk_mu')


# total number of the rich people
# by changing loan_interest
sns.lineplot(df_g, x='Step', y='Rich', hue='loan_interest')
# by changing reserve ratio
sns.lineplot(df_g, x='Step', y='Rich', hue='reserve_percent')
# by changing risk_mu
sns.lineplot(df_g, x='Step', y='Rich', hue='risk_mu')

# total number of the poor people
sns.lineplot(df_g, x='Step', y='Poor', hue='loan_interest')
# by changing reserve ratio
sns.lineplot(df_g, x='Step', y='Poor', hue='reserve_percent')
# by changing risk_mu
sns.lineplot(df_g, x='Step', y='Poor', hue='risk_mu')

g = sns.FacetGrid(df_g, col="loan_interest", row="risk_mu")
g.map(sns.histplot, "Wealth")


## 1.2 distribution of the wealth -------------------------------------------------
df100 = df[df['Step']==100]

# change loan_interest
sns.violinplot(df100, x='loan_interest', y='Wealth')
sns.kdeplot(df100, x='Wealth', hue ='loan_interest')

# change reservation ratio
sns.violinplot(df100, x='reserve_percent', y='Wealth')
sns.kdeplot(df100, x='Wealth', hue ='reserve_percent')

# change risk_mu
sns.boxplot(df100, x='risk_mu', y='Wealth')
sns.violinplot(df100, x='risk_mu', y='Wealth')
sns.kdeplot(df100, x='Wealth', hue ='risk_mu')

## 1.3 some metrics of inequality

test = df100.groupby(['RunId'])['loan_interest','reserve_percent','risk_mu',
                                  'Wealth','Rich','Poor','Middle Class'].mean().reset_index()
sdev = df100.groupby(['RunId'])['Wealth'].std().reset_index()
sdev.rename(columns={"RunId": "RunId2", "Wealth": "std_wealth"}, inplace=True)

df_name = pd.concat(
    [test, sdev],
    axis=1,
    ignore_index=False
)


sns.boxplot(df_name, x='reserve_percent', y='std_wealth')
sns.boxplot(df_name, x='loan_interest', y='std_wealth')
sns.boxplot(df_name, x='risk_mu', y='std_wealth')  

g = sns.FacetGrid(df_name, col="loan_interest", row="risk_mu")
g.map(sns.histplot, "Wealth")




