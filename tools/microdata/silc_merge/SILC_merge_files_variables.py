# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 10:03:08 2016

@author: arranda
"""
import glob
import os
import os.path
import pandas as pd
import re

#thedir='D:\\SILC\\Micro\\'
#thedir='C:\\Users\\smarkus\\Documents_local\\EUROSTAT_Microdata\\EU_SILC\\data\\'
thedir='C:\\Users\\franfab\\microdata\\EUSILC\\EUSILC unzipped\\'

subfolders=[ name for name in os.listdir(thedir) if os.path.isdir(os.path.join(thedir, name)) and name!='Final' ]

#This function produces a list of all files obtained after the unzipping procedure. Normally, they should be 4 files for each year, each country and each of the two collections (Cross and Long)
def files():
    files=pd.DataFrame(columns=['country', 'year','types','filename'])
    for folder in subfolders:
        os.chdir(thedir+folder)
        thedirC=thedir+folder
        countries=[ name for name in os.listdir(thedirC) if os.path.isdir(os.path.join(thedirC, name)) and name!='merged' ]
        print(countries)
        for ctry in countries:
            thedirCC=thedirC+'\\'+ctry
            os.chdir(thedirC+'\\'+ctry)
            years=[ name for name in os.listdir(thedirCC) if os.path.isdir(os.path.join(thedirCC, name)) and re.search(r'[2][0][0-2][0-9]',name) ] #only years beetwen 2000 and 2029 are allowed
            for year in years:
                os.chdir(thedirCC+'\\'+year)
                filelist = glob.glob("*.csv")
                print(filelist)
                tmp=pd.DataFrame(filelist)
                tmp.columns=['filename']
                tmp['country']=ctry
                tmp['year']=year
                tmp['types']=folder
                files=files.append(tmp)
    files.to_csv(thedir+'All_files_names.csv')

# This function produces a list of allvariables used in Cross and Long in all countries and all years
def variables():
    volume=pd.DataFrame(columns=['country', 'year','types','filename','length'])
    variables=pd.DataFrame(columns=['country', 'year','types','filename','variable'])
    for folder in subfolders:
        os.chdir(thedir+folder)
        thedirC=thedir+folder
        countries=[ name for name in os.listdir(thedirC) if os.path.isdir(os.path.join(thedirC, name)) and name!='merged' ]
        for ctry in countries:
            thedirCC=thedirC+'\\'+ctry
            os.chdir(thedirC+'\\'+ctry)
            years=[ name for name in os.listdir(thedirCC) if os.path.isdir(os.path.join(thedirCC, name)) and re.search(r'[2][0][0-2][0-9]',name) ] #only years beetwen 2000 and 2029 are allowed
            for year in years:
                os.chdir(thedirCC+'\\'+year)
                filelist = glob.glob("*.csv")
                print(filelist)
                thedirCCY=thedirCC+'\\'+year
                tmp2=pd.DataFrame(columns=['filename','variable'])
                tmp4=pd.DataFrame(columns=['filename','length'])
                for file in filelist:
                    d=pd.read_csv(thedirCCY+'\\'+file)
                    tmp1=pd.DataFrame(d.columns)
                    template=[['',0]]
                    tmp3=pd.DataFrame(template,columns=['filename','length'])
                    tmp1.columns=['variable']
                    tmp1['filename']=file
                    tmp2=tmp2.append(tmp1)
                    tmp3['filename']=file
                    tmp3['length']=len(d)
                    tmp4=tmp4.append(tmp3)
                tmp2['country']=ctry
                tmp2['year']=year
                tmp2['types']=folder
                tmp4['country']=ctry
                tmp4['year']=year
                tmp4['types']=folder
                variables=variables.append(tmp2)
                volume=volume.append(tmp4)
    variables.to_csv(thedir+'All_variables_names.csv')
    volume.to_csv(thedir+'All_sample_sizes.csv')
        
files()

variables()

