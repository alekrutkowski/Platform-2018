# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 14:12:10 2016

@author: arranda
"""

from formula_engine.engine_v2 import *
from util.tools import * 
from util.catalogues import *
from tools.sppm.substantive import *

startYear=2005
#EU28Countries=["EU28","EU27_2020","EA19","BE","BG","CZ","DK","DE","EE", "IE", "EL", "ES", "FR", "HR", "IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE", "UK"]
EU28Countries=["EU27_2020","EA19","BE","BG","CZ","DK","DE","EE", "IE", "EL", "ES", "FR", "HR", "IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE"]
#Get data and read configuration
def getDashboardData(catalogue_object, cat_non_standard, file_output):    
    catalogueFormulas(cat_non_standard)   
    mergedFile=catalogue_object.getAllData()
    mergedFile=pd.DataFrame(mergedFile,columns=['IndicatorID','geo','year','values','value_n','flag','file'])    
    #mergedFile['value_n']=mergedFile['value_n'].convert_objects(convert_numeric=True)    
    mergedFile['value_n']=pd.to_numeric(mergedFile['value_n'])
    mergedFile.to_csv(merged_path+file_output+'.csv',index=False, float_format='%.2f')
    #Sync folders
    #syncFolders(merged_path,merged_path_p)    
    return mergedFile
 
#typeOfChange pp or %
#changeDistance short or long
#indicatorData is a df with all the data for that country and that indicator
def getChange(typeOfChange, final_value, original_value, decimals, country, changeDistance,indicatorCountryData,myIndicator):   
        
    #Manage exceptions
    #TODO: Clean everyyear
    #Exceptions for ref Year
    #print(final_value, original_value, country)                  
    myChange="n.a."
    final_value=float(final_value)
    if original_value.empty==False and ~ np.isnan(original_value.iloc[0]):
        original_value=float(original_value)
    else:
        return myChange
    
    if typeOfChange=="pp":
        myChange=round(final_value-original_value,decimals)
    elif typeOfChange=="%":
        myChange=round(100*(final_value-original_value)/original_value,decimals)
    else:
        raise Exception("Type of change not defined")    
    return myChange
        
def getFlagChange(listOfFlags):
    return ''.join(set(''.join(listOfFlags)))
    

# Combine per indicator, country, indicator levels of significance (either from config or from ESTAT)
# with levels of sustantiveness (from config) and choose the higher value to check against the data 


def getSignificance_Sustantiveness(indicator, country, typeOfChange, senseOfChange, changeLength, value):
    if value=="n.a.":
        return "no"
        
    mySignificance=""
    #get significance and sustantiveness from rhw catalogue and choose the biggest one
    if changeLength=="short":
        mySignificance=np.nanmax([significance_short[indicator], substantiveness_short[indicator]])
    elif changeLength=="long":
        mySignificance=np.nanmax([significance_long[indicator], substantiveness_long[indicator]])
    
    #read significances from the file, for the moment significances from ESTAT are provided as boolean Yes/No    
    sig_flag=''
    sig=0
    if len(estatSignificances)>0:
        significance_ESTAT= estatSignificances[(estatSignificances.IndicatorID==indicator) & (estatSignificances.geo==country)]
        if len(significance_ESTAT)>0:
              significance_ESTAT=significance_ESTAT.iloc[0][changeLength+'_boolean']          
              if not pd.isnull(significance_ESTAT):        
                  sig_flag=significance_ESTAT     
                  sig=significance_ESTAT
     
    if abs(value)> mySignificance and abs(value)> sig and sig_flag!='No':
        if (senseOfChange=="pos" and value>0) or (senseOfChange=="neg" and value<0):
            return "positive"
        else:
            return "negative"
    return "no"
 
#Main thread
#Read configuration
myCatalogue=catalogue('catalogue - EPM_dashboard.csv')
#When significances load them, otherwise no significances
estatSignificances=pd.DataFrame()
estatSignificances=pd.read_csv("G:\\A4\\04 Data and tools\\Reports\\EPM Dashboard\\config\\EPM_significances2019.csv")

#get data  
data=getDashboardData(myCatalogue, 'catalogue - EPM_dashboard.csv','EPM_dashboard')

#calculate substantiviness
getSubstantive('EPM')
#reload catalogue with the latest substantiveness
myCatalogue=catalogue('catalogue - EPM_dashboard.csv')
sense=myCatalogue.getSpecialField("sense")    
changeType=myCatalogue.getSpecialField("change")
order=myCatalogue.getSpecialField("Order")
decimals=myCatalogue.getSpecialField("decimals")
description=myCatalogue.getSpecialField("Indicator")
significance_short=myCatalogue.getSpecialField("significance_short")
significance_long=myCatalogue.getSpecialField("significance_long")
substantiveness_short=myCatalogue.getSpecialField("substantiveness_short")
substantiveness_long=myCatalogue.getSpecialField("substantiveness_long")

data=data[data.geo.isin(EU28Countries)]
AllData=data.copy()

#loop per indicator
dashboard=pd.DataFrame()
indicators=data.groupby(by=['IndicatorID'])
refYear=""
dashboardData={}
for nme, gr in indicators:
    myIndicator=nme
    #print(name)
    type_of_change=changeType[myIndicator]
    type_of_sense=sense[myIndicator]
    number_of_dec=decimals[myIndicator]
    
    indicatorData=pd.DataFrame(gr)
    if len(indicatorData[(indicatorData.value_n.notnull()) & (indicatorData.year==max(indicatorData['year']))])>14:
        refYear=max(indicatorData['year'])
    else:
        refYear=max(indicatorData['year'])-1
    
    
    myData=[myIndicator,description[myIndicator], refYear, type_of_change]
    dictDataIndicators={}
        
    indCountryData=indicatorData.groupby(by=['geo'])
    for name, group in indCountryData:
        country=name               
        refValue =  refFlag = short_flag =  long_flag = extraFlag = ""        
        short_change  = long_change ="n.a."
        significanceShort = significanceLong = "no"      
        
        
        #Ref Value/Flag
        if refYear!="":
            if len(group[(group.value_n.notnull()) & (group.year==refYear)])>0:
                refValue=float(group[group.year==refYear].iloc[0]['value_n'])
                refFlag=group.fillna("")[group.year==refYear].iloc[0]['flag']            
            if refValue=="" and len(group[(group.value_n.notnull()) & (group.year==(refYear-1))])>0:
                extraFlag="("+str(refYear-1)+")" 
                refValue=float(group[group.year==(refYear-1)].iloc[0]['value_n'])
                refFlag=group.fillna("")[group.year==(refYear-1)].iloc[0]['flag']+extraFlag
        
                
        #Calculate changes, long and short,  correspondant flags and Assesing change     
        if refYear!="" and refValue!="": 
            #Short
            if extraFlag=="":            
                short_change=getChange(type_of_change,refValue,group['value_n'][group.year==(refYear-1)],1, country, 'short',group,myIndicator)
                short_flag=getFlagChange(list(group['flag'][(group.year.isin([refYear,(refYear-1)])) & (group.flag.notnull())]))
                significanceShort=getSignificance_Sustantiveness(myIndicator,country,type_of_change,type_of_sense, 'short', short_change)
                
            #Long
            if len(group[(group.year==(refYear-3)) & (group.value_n.notnull())])==1:            
                long_change=getChange(type_of_change,refValue,group['value_n'][group.year==(refYear-3)],1, country, 'long',group,myIndicator)
                #The important flag is the 'b' flag an in this case we don't need to go up to 3 years before, but 2, in a change between 14 and 17 a 'b' in 14 is irrelevant
                long_flag=getFlagChange(list(group['flag'][(group.year>(refYear-3))&(group.flag.notnull())]))+extraFlag
                significanceLong=getSignificance_Sustantiveness(myIndicator,country,type_of_change,type_of_sense, 'long', long_change)
                
        #TODO: Exceptional cases to be treated
        #decimals
        if refValue!="":
            formatter="{:."+str(number_of_dec)+"f}"
            refValue=formatter.format(refValue)
        else:
            refValue="n.a."
            
        #Cosmetic changes
        if significanceShort=="no" and refValue!="n.a." and short_change!="n.a.":
            short_change="~"
        if significanceLong=="no"  and refValue!="n.a." and long_change!="n.a.":
            long_change="~"
            
        #Output      
        dictDataIndicators[country]=[refValue,refFlag,short_change,short_flag,significanceShort,long_change,long_flag, significanceLong]
    myData.append(dictDataIndicators)
    dashboardData[order[myIndicator]]=myData
    
    #print(dashboardData)
    #break


