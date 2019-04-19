#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 21:08:22 2019

@author: jiayilin
"""
#A script to show distributions of win rates

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

count_preflop = 20
winrate_list_preflop = []

count_threecards = 15
winrate_list_threecards = []

count_fourcards = 10
winrate_list_fourcards = []

count_fivecards = 5
winrate_list_fivecards = []
with open('rl_data.txt','r') as file:

    for line in file:
        if line == "\n":
            pass
        else: 
            count_preflop = count_preflop+1
            count_threecards=count_threecards+1
            count_fourcards=count_fourcards+1
            count_fivecards=count_fivecards+1
            if count_preflop %21 ==0:
                winrate_list_preflop.append(float(line))
            if count_threecards %21 ==0:
                winrate_list_threecards.append(float(line))
            if count_fourcards %21 ==0:
                winrate_list_fourcards.append(float(line))
            if count_fivecards %21 ==0:
                winrate_list_fivecards.append(float(line))
winrate_list_preflop = np.array(winrate_list_preflop)
winrate_list_threecards = np.array(winrate_list_threecards)
winrate_list_fourcards = np.array(winrate_list_fourcards)
winrate_list_fivecards = np.array(winrate_list_fivecards)
plt.figure(0)
sns.distplot(winrate_list_preflop);
plt.figure(1)
sns.distplot(winrate_list_threecards);
plt.figure(2)
sns.distplot(winrate_list_fourcards);
plt.figure(3)
sns.distplot(winrate_list_fivecards);

#%%
## find the correlation between win rates 
print np.corrcoef(winrate_list_preflop,winrate_list_fivecards)
print np.corrcoef(winrate_list_threecards,winrate_list_fivecards)
print np.corrcoef(winrate_list_fourcards,winrate_list_fivecards)