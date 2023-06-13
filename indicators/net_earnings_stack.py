# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 11:58:22 2018

@author: franfab
"""

import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from parameters import *

#define source and destination paths if different from "original" and "calculated". In that case, change the reference in the formulas
#source_path = 'C:\\Data\\non_standard\\original\\'
#destination_path = 'C:\\Data\\non_standard\\calculated\\'

#save the data sheet from the original Excel to CSV
df = pd.read_csv(original_path + 'For Fabio test.csv') #change file name into net_earnings.csv

c = df.columns[0]
years = df.columns[1:]
df1 = df.unstack(level = 1)

#extract and stack yearly data
d={}
for i in years:
    d["year" + str(i)] = df1[i]
for i in d:
     y = pd.concat(d)
y = y.reset_index(level=0)

countries = pd.DataFrame(data=df1[c])

netearn = pd.merge(countries, y, left_index=True, right_index=True)
netearn.columns = ['geo', 'year', 'value_n']

def my_func(list, f):
    return[f(x) for x in list]
netearn['year'] = my_func(netearn['year'], lambda x: x[-4:])
netearn['year'].astype(np.int64)

netearn['IndicatorID'] = "ID12"

netearn_clean = netearn.dropna()
netearn_clean.to_csv(calculated_path + 'net_earnings_TEST.csv', index=False)


#David's code
#a= pd.read_csv(original_path+f+'.csv')    
#a=a.set_index(['Row Labels'])
#b=a.stack()
#b=b.reset_index()
#b.columns=['geo','year','value_n']