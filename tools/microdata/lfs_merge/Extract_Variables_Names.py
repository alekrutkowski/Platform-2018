# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 17:17:02 2019

@author: badeape
"""

from pandas import Series, DataFrame
import pandas as pd
import config.config_LFS

Years = ['2009','2010','2011','2012','2013','2014','2015','2016','2017']

df = pd.DataFrame()
for year in Years:
    print(year)
    data = pd.read_csv(local+'YearlyData_'+str(year)+'.csv')
    tmp = pd.DataFrame(list(data))
    tmp['year'] = year
    df = df.append(tmp)

df.to_csv(localExt+'LFS_variables names.csv')