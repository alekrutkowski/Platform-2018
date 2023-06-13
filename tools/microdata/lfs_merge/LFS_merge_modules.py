# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 10:03:08 2016

@author: badeape
"""
import glob
import os
import os.path
import pandas as pd

years = ['2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2016','2017','2018']
# Ad-hoc modules
thedir='D:\\LFS\\AHM2017-2018\\AdhocModules.ver2\\'

os.chdir(thedir)
filelist = glob.glob("*.csv")
for year in years:
    modulesLFS=pd.DataFrame()
    for file in filelist:
        if year == file[2:6]:
            print(file)
            df=pd.read_csv(thedir+file)
            print('Year: '+year+', No of columns: '+str(len(list(set(df.columns)))))
            modulesLFS=modulesLFS.append(df)
    modulesLFS.to_csv(thedir+'AdhocModule_'+str(year)+'.csv')    
    
