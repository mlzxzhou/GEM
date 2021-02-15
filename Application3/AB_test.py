
# coding: utf-8
import numpy as np
import pandas as pd

from scipy.stats import ttest_ind, ttest_1samp
from scipy.stats.mstats import winsorize
from scipy.stats import boxcox
from scipy.stats import norm, t
from scipy.stats.kde import gaussian_kde
from scipy.linalg import block_diag
from scipy.stats import chi2

import statsmodels.api as sm
import statsmodels.formula.api as smf

import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="whitegrid", palette="pastel", color_codes=True)
import os
import warnings
warnings.filterwarnings("ignore")
from itertools import product
import multiprocessing as mp
import sys
from vcm_model import VCM


metric_data_path = 'data/ab_test/area5/'

######################################
#### Generate results in Table 3  ####
######################################

### AA test
print('AA test\n')

df = pd.read_csv(metric_data_path + 'data_cost_lambda_eq1.csv',
                 parse_dates=['dt'], 
                 index_col=['dt','minute_strive'])
df.sort_index(inplace=True)
df.index.names = ['date','minute_strive']
df.drop('Unnamed: 0', axis=1, inplace=True)

outs = np.load(metric_data_path + 'out0_new.npy')
df['sdi'] = outs[:,0]
df['metric'] = outs[:,1]
df['answer_rate'] = outs[:,2]
df['order_cnt'] = outs[:,3]
df['driver_cnt'] = outs[:,4]

df = df.reset_index()
df['hour'] = df['minute_strive'].apply(lambda string: string.split(':')[0]).astype(np.int)
df['minute'] = df['minute_strive'].apply(lambda string: string.split(':')[1]).astype(np.int)
df['time'] = (df['hour'] * 60 + df['minute'])//30

df['order_cnt_x_metric'] = df['order_cnt'] * df['metric']

df = df.groupby(['date','time']).sum()
df['w_metric'] = df['order_cnt_x_metric'] / df['order_cnt']

file = 'V1_hangzhou_serial_order_dispatch_AA.csv'

df2 = pd.read_csv(metric_data_path + file, index_col=['date','time'], parse_dates=['date']).sort_index()

df2['metric'] = df['metric'].values

df = df2.copy()


ycols = ['cnt_grab','cnt_finish','metric']
xcols = ['cnt_call']
acol = 'is_exp'

for ycol in ycols:

    model = VCM(df, ycol, xcols, acol)
    model.inference()

    base = df.loc[df['is_exp']==-1].groupby('date')[ycol].sum().mean()
    ratio = model.holder['gamma'] / base
    print(ycol, ratio*100, model.holder['pvalue1'], model.holder['pvalue2'], '\n')
    
    
### AB test
print('AB test\n')
df = pd.read_csv(metric_data_path + 'data_cost_lambda_eq1.csv', 
                 parse_dates=['dt'], 
                 index_col=['dt','minute_strive'])
df.sort_index(inplace=True)
df.index.names = ['date','minute_strive']
df.drop('Unnamed: 0', axis=1, inplace=True)

outs = np.load(metric_data_path + 'out1_new.npy')
df['sdi'] = outs[:,0]
df['metric'] = outs[:,1]
df['answer_rate'] = outs[:,2]
df['order_cnt'] = outs[:,3]
df['driver_cnt'] = outs[:,4]

df = df.reset_index()
df['hour'] = df['minute_strive'].apply(lambda string: string.split(':')[0]).astype(np.int)
df['minute'] = df['minute_strive'].apply(lambda string: string.split(':')[1]).astype(np.int)
df['time'] = (df['hour'] * 60 + df['minute'])//30

df['order_cnt_x_metric'] = df['order_cnt'] * df['metric']

df = df.groupby(['date','time']).sum()
df['w_metric'] = df['order_cnt_x_metric'] / df['order_cnt']

file = 'V1_hangzhou_serial_order_dispatch_AB.csv'

df2 = pd.read_csv(metric_data_path + file, index_col=['date','time'], parse_dates=['date']).sort_index()

df2['metric'] = df['metric'].values

df = df2.copy() 

ycols = ['cnt_grab', 'cnt_finish', 'metric']
xcols = ['cnt_call']
acol = 'is_exp'

for ycol in ycols:

    model = VCM(df, ycol, xcols, acol)
    model.inference()

    base = df.loc[df['is_exp']==-1].groupby('date')[ycol].sum().mean()
    ratio = model.holder['gamma'] / base
    print(ycol, ratio*100, model.holder['pvalue1'], model.holder['pvalue2'], '\n')

########################
### Plot Figure 7(A) ###
########################

ycol = 'metric'

dft = df.loc['2018-12-08', ['is_exp', ycol]].reset_index()

idices0 = dft['is_exp']==-1
idices1 = dft['is_exp']==1

fig, ax = plt.subplots(1, 1, figsize=(15, 4))

ax.scatter(dft.loc[idices0, 'time']+1, dft.loc[idices0, ycol], color='green', label='Ctrl')
ax.scatter(dft.loc[idices1, 'time']+1, dft.loc[idices1, ycol], color='red',   label='Exp')

ax.set_xlabel('Time (half hour)', fontsize=15)
ax.set_ylabel('Metric', fontsize=15)
ax.legend(loc='upper left', fontsize=15)
ax.set_title('Metric of 20181208', fontsize=20)

plt.savefig(metric_data_path + 'metric_resid_AB_20181208.png', dpi=200, bbox_inches='tight')


