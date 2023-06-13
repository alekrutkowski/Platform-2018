# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 16:51:19 2017

@author: badeape
"""

from pandas import Series, DataFrame
import pandas as pd
import glob
import os
import os.path
import config.config_LFS

files = os.listdir(local)
dataset=pd.DataFrame()
for file in files:
    data=pd.read_csv(local+file)
    data=data[variables]
    data.to_csv(localExt + outFile + file)
    dataset=dataset.append(data)
    print(file)

dataset['COUNTRY'].replace('GR','EL',inplace=True)
dataset=dataset[dataset.COUNTRY.isin(CtryList)]    
dataset.to_csv(localExt + outFile + '.csv')