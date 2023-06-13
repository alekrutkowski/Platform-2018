# -*- coding: utf-8 -*-
"""

@author: franfab
"""
import glob
import os
import os.path
import pandas as pd

#years = ['2002','2006','2010','2014','2018']
years = ['2018']
ctrylist = ['AT','BE','BG','CY','CZ','DE','DK','EE','EL','ES','FI','FR','HR','HU','IS','IT','LT','LU','LV','MT','NL','NO','PL','PT','RO','SE','SI','SK','UK']

# Yearly files
thedir="C:\\Users\\franfab\\microdata\\SES\\SES_2002-2018_original"

os.chdir(thedir)
sesctry = os.listdir(thedir)

for year in years:

    yearSES=pd.DataFrame()

    for ctry in ctrylist:
        if ctry in sesctry:
            os.chdir(thedir + "\\" + ctry)
            filelist = glob.glob("*.csv")

            for file in filelist:
                if year == file[7:11]:
                    print(file)
                    df = pd.read_csv(thedir + "\\" + ctry + "\\" + file)
                    print('Year: ' + year + ', No of columns: ' + str(len(list(set(df.columns)))))
                    if str(len(list(set(df.columns)))) == 1:
                        df = df.str.split(pat=";", expand=True)
                    yearSES=yearSES.append(df)

    print("")
    print('Saving ' + 'SES_YearlyData_' + str(year))
    yearSES.to_csv(thedir + 'SES_YearlyData_' + str(year) + '.csv')
    
    
#test    
#df = pd.read_csv(thedir + "\\SK\\SES_SK_2018_ANONYM_CD.csv")
#if str(len(list(set(df.columns)))) == 1:
    #df = df[df.columns[0]].str.split(pat=";", expand=True)

