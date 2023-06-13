# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 10:03:08 2016

@author: badeape
"""
import glob
import os
import os.path
import pandas as pd

years = ['1983','1984','1985','1986','1987','1988','1989','1990','1991','1992','1993','1994','1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005']#

#years = ['2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021']


# Yearly files
thedir='C:\\Users\\franfab\\microdata\\LFS\\NEW data structure 1983-2021\\working\\'

os.chdir(thedir)
filelist = glob.glob("*.csv")
for year in years:
    yearLFS=pd.DataFrame()
    for file in filelist:
        if year == file[2:6]:
            print(file)
            df=pd.read_csv(thedir+file)
            print('Year: '+year+', No of columns: '+str(len(list(set(df.columns)))))
            yearLFS=yearLFS.append(df)
    yearLFS.to_csv(thedir+'YearlyData_'+str(year)+'.csv')
