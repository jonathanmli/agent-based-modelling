# libraries
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from PIL import Image

sns.set_style("whitegrid")

# get buatch run data
df = pd.read_csv('data/data.csv') # original model

df.columns

"""
br_params = {
    "init_people": [100],
    "rich_threshold": [10],
    "reserve_percent": [0, 20, 40],
    "loan_interest": [1, 2, 3],
    "risk_mu": [3,5,7],
    "risk_sigma": [5]
}
"""

df.columns

## 1.1 the effect on aggregated data-------------------------------------------
# the effect on the average wealth
df_g = df.groupby(['RunId','Step'])['loan_interest','reserve_percent','risk_mu',
                                  'Wealth','Rich','Poor','Middle Class','gini','gini2'].mean().reset_index()


pal2 = sns.cubehelix_palette(start=0, rot=0, dark=0.1, light=.7, as_cmap=True)
pal3 = sns.cubehelix_palette(start=1, rot=0, dark=0, light=.7, as_cmap=True)


sns.set(font_scale=1.5)

# total wealth path
# by changing loan_interest
fig, ax = plt.subplots(figsize=(9,6))
sns.lineplot(df_g, x='Step', y='Wealth',
             hue='loan_interest', palette=pal2).set(title='the effect of interest rate on total wealth')
plt.savefig('plots/path_wealth_interestrate.png')

# by changing reserve ratio
fig, ax = plt.subplots(figsize=(9,6))
sns.lineplot(df_g, x='Step', y='Wealth', hue='reserve_percent').set(title='the effect of reserve ratio on total wealth')
plt.savefig('plots/path_wealth_reserveratio.png')

# by changing risk_mu
fig, ax = plt.subplots(figsize=(9,6))
sns.lineplot(df_g, x='Step', y='Wealth',
             hue='risk_mu', palette=pal3).set(title='the effect of risk asset on total wealth')
plt.savefig('plots/path_wealth_risk_mu.png')


## 1.2 distribution of the wealth -------------------------------------------------
df100 = df[df['Step']==100]
sns.set(font_scale=1.5)
# change loan_interest
fig, ax = plt.subplots(figsize=(9,6))
sns.kdeplot(df100, x='Wealth',
            hue ='loan_interest', palette=pal2).set(title='the effect of interest rate on wealth distribution')
ax.set(xlabel='Wealth (after 100 steps)')
plt.savefig('plots/wealth_distribution_interestrate.png')

# change reservation ratio
fig, ax = plt.subplots(figsize=(9,6))
sns.kdeplot(df100, x='Wealth', hue ='reserve_percent').set(title='the effect of reserve ratio on wealth distribution')
ax.set(xlabel='Wealth (after 100 steps)')
plt.savefig('plots/wealth_distribution_reserveratio.png')

# change risk_mu
fig, ax = plt.subplots(figsize=(9,6))
sns.kdeplot(df100, x='Wealth', hue ='risk_mu',
            palette=pal3).set(title='the effect of risk asset on wealth distribution')
ax.set(xlabel='Wealth (after 100 steps)')
plt.savefig('plots/wealth_distribution_risk_mu.png')

##1.3 gini index in total savings -------------------------------------------------
df100_g =df_g[df_g['Step']==100]

# gini of the risk mu
fig, ax = plt.subplots(figsize=(8,6))
sns.boxplot(data=df100_g, y='gini',x='risk_mu').set(title='the effect of risk asset on gini index')
ax.set(ylabel='gini_index')
plt.savefig('plots/gini_risk_mu.png')

# gini of the risk mu
fig, ax = plt.subplots(figsize=(8,6))
sns.boxplot(data=df100_g, y='gini2',x='loan_interest').set(title='the effect of loan interest on gini index')
ax.set(ylabel='gini_index')
plt.savefig('plots/gini_loan_interest.png')

## 1.4 ----------------------------------------------------------------------------
# combine plots for the paper
# combine png
def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

#
im1 = Image.open('plots/path_wealth_interestrate.png')
im2 = Image.open('plots/wealth_distribution_interestrate.png')

get_concat_h(im1, im2).save('plots/interestrate.png')
#
im1 = Image.open('plots/path_wealth_reserveratio.png')
im2 = Image.open('plots/wealth_distribution_reserveratio.png')

get_concat_h(im1, im2).save('plots/reserveratio.png')
#
im1 = Image.open('plots/path_wealth_risk_mu.png')
im2 = Image.open('plots/wealth_distribution_risk_mu.png')

get_concat_h(im1, im2).save('plots/risk_mu.png')

#
im1 = Image.open('plots/gini_risk_mu.png')
im2 = Image.open('plots/gini_loan_interest.png')

get_concat_h(im1, im2).save('plots/gini.png')

