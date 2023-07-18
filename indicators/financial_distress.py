# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 15:30:15 2014

@author: arranda
"""

import pandas as pd
from util.download_data import *
from config.parameters import *

#normally the file sent by ECFIN is named e.g. "DG_EMPL_detailed_data_EU_updated Feb 2019.xls"
original=pd.ExcelFile(original_path+'DG_EMPL_financial_distress.xls')

def getPrefix(sheet):
    if sheet=='EU':
        return 'TOT'
    else:
        return sheet[-3:]
    
#1ST PART: 
#A)EXTRACT ALL THE EU VALUES:Question 12 
#B)calculte the EU agregates Question12 M+MM 
outputFile='financialDistress_EUdetails'

sheets=['EU','EU_RE1','EU_RE2','EU_RE3','EU_RE4','EU_ED1','EU_ED2','EU_ED3','EU_AG1','EU_AG2','EU_AG3','EU_AG4','EU_MAL','EU_FEM']
merged=pd.DataFrame()
EUaggregate=pd.DataFrame()

for sh in sheets:   
    #START NEW   
    EU=original.parse(sh, header=[0,1]) 
    d=EU[12]
    
    #workaround for date column, make it more elegant
    dates=EU['Question number:']
    d = pd.merge(dates, d, left_index=True, right_index=True)
    d = d.set_index('Category of reply:')
    
    #Check this are the right columns
#    if list(set(c.columns.get_level_values(0)))[0]!=12:       
#        print("PROBLEM WITH COLUMN NAMES")
#    d=c.copy()
#    d.columns=d.columns.droplevel()
   
    myColumns=list(d.columns)
    prefix=getPrefix(sh)    
    for i in range(len(myColumns)):
        myColumns[i]=prefix+".12."+myColumns[i]
    d.columns=myColumns
    
    e=d.stack()
    e=e.reset_index()
    e.columns=['date','indicator','value_n']
       
    #AGREGATE values for the EU from answers M and MM 
    EU_M_MM =d.copy()
    cols=EU_M_MM.columns
    EU_M_MM['geo']='EU27'
    EU_M_MM['indicator']=prefix    
    EU_M_MM['value_n']=EU_M_MM[prefix+".12."+"M"]+ EU_M_MM[prefix+".12."+"MM"]    
    EU_M_MM=EU_M_MM.drop(cols, axis=1)
    
    
    if merged.empty:
        merged=e.copy()
        EUaggregate=EU_M_MM.copy()        
    else:
        merged=merged.append(e)
        EUaggregate=EUaggregate.append(EU_M_MM)
    
a=merged.copy()
a.columns=['date','indicator','value_n']
a['geo']='EU27'
a['date']=a['date'].map(str)
a['year']=a['date'].str[0:4]
a['month']=a['date'].str[5:7]
a['month']=a['month'].map(int)
a['file']=outputFile
a['value_n']=a['value_n'].map(float)
a.to_csv(calculated_path+outputFile+'.csv',index=False, float_format='%.2f')

#2ND PART: EXTRACT ALL THE COUNTRY AGREGATES
outputFile='financialDistress'

# The Excel contains 2 sheets with the values
original_1=original.parse('financial stress by country1', header=[1,2])
original_2=original.parse('financial stress by country2', header=[1,2])

merged=pd.DataFrame()
for ori_data in [original_1,original_2]:
    data=ori_data.copy()
    
    #workaround for date column, make it more elegant
    #"dates" comes from 1st part
    d = pd.merge(dates, data, left_index=True, right_index=True)
    d = d.set_index('Category of reply:')
    data = d.drop(('Unnamed: 0_level_0', 'Unnamed: 0_level_1'),axis=1)        
    a = data.stack()
    #a = a.stack() This was needed in previous routine
    a = a.reset_index()
    g = pd.DataFrame(a['level_1'].values.tolist(), index=a.index)
    a = pd.merge(a,g,left_index=True, right_index=True)
    a = a.drop('level_1', axis=1)
    
    a.columns=['date','value_n','geo','indicator']
    if merged.empty:
        merged=a.copy()
    else:
        merged=merged.append(a)

#ADD EU AGGREGATES
b=merged.copy()
EUaggregate=EUaggregate.reset_index()
EUaggregate.columns=['date','geo','indicator','value_n']
b=b.append(EUaggregate)

b['date']=b['date'].map(str)
b['year']=b['date'].str[0:4]
b['month']=b['date'].str[5:7]
b['month']=b['month'].map(int)
b['file']=outputFile
b['value_n']=b['value_n'].map(float)

#Add aggregate for EU27
b.to_csv(calculated_path+outputFile+'.csv',index=False, float_format='%.2f')





