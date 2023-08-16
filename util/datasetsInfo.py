# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 15:39:03 2014
This module access the sqlite database that contains the information provided by Eurostat
This information is refreshed automatically by the Task in Navicat

@author: arranda
"""

from  config.parameters import *
import glob, os
import os.path


try:
    DATA_INFO=pd.read_csv('https://ec.europa.eu/eurostat/api/dissemination/catalogue/toc/txt?lang=EN', sep='\t', on_bad_lines='skip') # warn_bad_lines=False, error_bad_lines=False) # See https://stackoverflow.com/a/74276812
    DATA_INFO.to_csv(stacked_path+"dataset_info.csv")
except Exception as e:
    print("ERROR:"+str(e))
 

def getInfo(dataset):
    if dataset in list(DATA_INFO["code"]):
        return str(DATA_INFO["title"][DATA_INFO.code==dataset].iloc[0]).strip()
    else:
        return ""
        
def getUpdateDate(dataset):
    if dataset in list(DATA_INFO["code"]):
        return str(DATA_INFO["last update of data"][DATA_INFO.code==dataset].iloc[0]).strip()
    else:
        return ""
    
def createSchemaIni():
    #subfolders=[ name for name in os.listdir(stacked_path) if os.path.isdir(os.path.join(stacked_path, name)) ]

    #for i in subfolders:
    os.chdir(stacked_path)
    filelist = glob.glob("*.csv")
    file = open(stacked_path+"\\Schema.ini", "w")
    for f in filelist:                           
        file.write("["+f+"]")
        file.write("\nColNameHeader=True\n")
        file.write("MaxScanRows=0\n")
        file.write("CharacterSet=65001\n")
    file.close()

createSchemaIni()



