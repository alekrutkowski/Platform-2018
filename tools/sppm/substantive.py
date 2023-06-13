# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 16:12:41 2016

@author: arranda
"""

import pandas as pd
import  numpy as np

#Load data and configuration
CtryList=['AT','BE','BG','CY', 'CZ','DE','DK','EE','EL','ES','FI','FR','HR','HU','IE','IT','LT','LU','LV','MT','NL','PL','PT','RO','SE','SI','SK']
#path='G:\\A4\\04 Data and tools\\Reports\\EPM_SPPM_analysis\\'

#First paramter is the cut-off point of outliers, second parameter is the Standard deviation multiple to be used as threshold
Substantive_Parameters=[0.075,1]

#dashboard could be EPM or SPPM
#This function updates the substantive columns in the different catalogues
def perch_ch_short(group):
    group['change_short_%']=100*(group['value_n']-group['value_n'].shift(1))/group['value_n'].shift(1)
    return group

def perch_ch_long(group):
    group['change_long_%']=100*(group['value_n']-group['value_n'].shift(7))/group['value_n'].shift(7)
    return group

def getSubstantive(dashboard):    
    cut_off=Substantive_Parameters[0]
    stadDev=Substantive_Parameters[1] 
    changesGap=['short','long']
    if dashboard=='EPM':
        path_cat='\\\\net1.cec.eu.int\\EMPL\\F\\F4\\04 Data and tools\\catalogues\\catalogue - EPM_dashboard.csv'
        a=pd.read_csv('H:\\Data\\merged\\EPM_dashboard.csv')
        longPeriod=3                
    elif dashboard=='SPPM':
        path_cat='\\\\net1.cec.eu.int\\EMPL\\F\\F4\\04 Data and tools\\catalogues\\catalogue - SPPM_dashboard.csv'        
        a=pd.read_csv('H:\\Data\\merged\\SPPM_dashboard.csv')
        longPeriod=7 # This is NOT the difference between the current year and 2008      
#    else:
#        print("ERROR, type of dashboard not correctly specified")
#        return
    catalogue=pd.read_csv(path_cat)
    catalogue=catalogue.set_index(['IND_CODE'])
    
    #Filter the data: since 2005,  only EU countries    
    a=a[a.geo.isin(CtryList)]
    a=a[a.year>2005]
    #Calculate changes
    a=a.sort_values(by=['year'])
    a['change_short_pp'] = a.groupby(['IndicatorID','geo'])['value_n'].diff(1)
#    a['change_short_%'] = a.groupby(['IndicatorID','geo'])['value_n'].pct_change(periods=1)*100
    a=a.groupby(['IndicatorID','geo']).apply(perch_ch_short)    
    
    #TODO change column names to make them generic
    a['change_long_pp'] = a.groupby(['IndicatorID','geo'])['value_n'].diff(longPeriod)
#    a['change_long_%'] = a.groupby(['IndicatorID','geo'])['value_n'].pct_change(periods=longPeriod)*100
    a=a.groupby(['IndicatorID','geo']).apply(perch_ch_long)
    
    # Delete breaks
    a=a[a.flag!='b'] 
    b=a.sort_values(by=['IndicatorID','geo'])
    
    #Create the distribution of absolute values
    for type_chg in ['short_pp','short_%','long_pp','long_%']:
        b['change_'+type_chg+'_abs']=b['change_'+type_chg].abs()   
    
    # Per indicator
    for ind in catalogue.index:    
        #get Indicator
        myIndicator=b[b.IndicatorID==ind]
        #Limit to the last 10 years of data
        myIndicator=myIndicator[myIndicator.year>=(max(myIndicator.year)-10)]
        
        #HGet the type of change and the senseof the indicator
        myChange= catalogue.loc[ind]['change']
        mySense= catalogue.loc[ind]['sense']
        myDescription=catalogue.loc[ind]['Indicator']
    
        #Create a 1y distribution and a 3y distribution
        dist_short='' # It will be  a dataframe containing the short changes
        dist_long=''  # It will be  a dataframe containing the long changes
        if myChange=='pp':
            dist_short =pd.DataFrame(myIndicator, columns=['IndicatorID', 'geo', 'year', 'values', 'value_n', 'flag', 'file','change_short_pp_abs', 'change_short_pp'])
            dist_long=pd.DataFrame(myIndicator, columns=['IndicatorID', 'geo', 'year', 'values', 'value_n', 'flag', 'file','change_long_pp_abs','change_long_pp'])
        elif myChange=='%':
            dist_short =pd.DataFrame(myIndicator, columns=['IndicatorID', 'geo', 'year', 'values', 'value_n', 'flag', 'file','change_short_%_abs','change_short_%'])
            dist_long=pd.DataFrame(myIndicator, columns=['IndicatorID', 'geo', 'year', 'values', 'value_n', 'flag', 'file','change_long_%_abs','change_long_%'])
        else:
            print("Wrong change type in configuration")
       
        for years in changesGap:
            #print(years)
            columnName='change_'+years+'_'+myChange+'_abs'
            distribution=eval('dist_'+years)
            distribution=distribution[~distribution[columnName].isnull()]
            #Remove the outliers defined by the cut off point
            myCutPoint=distribution[columnName].quantile([1-cut_off]).iloc[0]
            distribution=distribution[distribution[columnName]<myCutPoint]
            #Calculate std
            myStd=distribution[columnName].std(ddof=0)*stadDev
            #myStd=distribution[columnName].std()*stadDev 
            print(years+"--"+ind+"--"+str(myStd))
            #catalogue.set_value(ind,'substantiveness_'+years,myStd) #REMOVED FROM PANDAS 1.0.0
            catalogue.at[ind,'substantiveness_' + years] = myStd
    #Update the catalogue
    catalogue.to_csv(path_cat)
       
#getSubstantive('EPM')
