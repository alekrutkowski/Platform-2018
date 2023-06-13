# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 16:27:17 2015

@author: arranda
"""
import csv
import sys
import numpy as np
import sqlite3


from util.download_data import *


def remove_duplicates(s):    
    result = ""
    if type(s) is str:    
        dic = {}
        for i in s:
            if i not in dic:
                result+=i
                if ord(i.lower()) >= ord('a') and ord(i.lower()) <= ord('z'):
                    dic[i] = 1
    return result

# dimension is an array of dimensions
#letter=[a,b,c,d...]
# years_back must be negative
def getFactorData(dataset, dimensions, letter, years_back=0,):  
    #print(dataset)
                  
    if getInfo(dataset)!="":
        download_and_stack([dataset])
        data=pd.read_csv(stacked_path+dataset+'.csv')   
    else:
        data=pd.read_csv(calculated_path+dataset+'.csv')
        
    #Filter data dimensions
    indicatorData=data.copy()
    #aproximatin to the data dimensions (all the dimensions - year, geo, file, value, value_n, flag)
    aproxDimensions=len(indicatorData.columns)-6    
    
    #Maybe this will not work with non-standard files
    if (len(dimensions)<aproxDimensions):
        print("WARNING --- Maybe dimensions missing")
    
    for i in range(len(dimensions)):
        dim=(dimensions[i].split('=')[0]).strip()
        val=(dimensions[i].split('=')[1]).strip()            
        indicatorData[dim]=indicatorData[dim].astype(str)            
        indicatorData=indicatorData[(indicatorData[dim]==val)]        
    
    if max(indicatorData.groupby(['geo','year']).size())>1:
        raise Exception("TOO MUCH VALUES. Dimensions bad defined for:"+indicatorID)       
    
    if years_back<0:
        if "Q" in str(indicatorData.iloc[0]['year']):
            indicatorData['y']=indicatorData['year'].str[0:4].map(int)+(-1)*years_back
            indicatorData['q']=indicatorData['year'].str[4:]
            indicatorData['year']=indicatorData['y'].map(str)+indicatorData['q']            
        else:
            indicatorData['year']=indicatorData['year']+(-1)*years_back
     
    
    indicatorData['V_'+letter]= indicatorData['value_n']
    indicatorData['F_'+letter]= indicatorData['flag'].astype(str)
    indicatorData['F_'+letter]= indicatorData['F_'+letter].replace('nan','')
    
    # Return only geo, year, value_n and flag
    indicator=pd.DataFrame(indicatorData,columns=['geo','year','V_'+letter,'F_'+letter])
    
    return indicator        


#formula in the form of a+b
# factors as an array [a,b,c,d,...]
#Each factor is an array [dataset,[dimensions], years_back]
def calculateIndicator(formula, factors):
    letters=['a','b','c','d','e','f','g','h','i','j','k','l','m','n']
    newFormula=formula
    newFlag=''
    ALL=pd.DataFrame()
    #print(formula)
    #print(factors)
#TODO: validate that at least 2 factors exist
#TODO: letters and number of factors match    
    #loop factors
    for i in range(len(factors)):
        #get data
        if len(factors[i])>2:
            factorData = getFactorData(factors[i][0],factors[i][1],letters[i],factors[i][2])
        else:
            factorData = getFactorData(factors[i][0],factors[i][1],letters[i])
        #join data
        if ALL.empty:
            ALL=factorData.copy()
        else:
            ALL=pd.merge(ALL,factorData, on=['geo','year'])   
        
        newFormula=newFormula.replace(letters[i],"ALL['V_"+letters[i]+"']")        
        newFlag=newFlag+"+ALL['F_"+letters[i]+"']"
        #print(newFormula)
    
    #print(newFormula)   
    #execute formula     
    exec("ALL['value_n']="+newFormula)
    exec("ALL['flag']="+newFlag[1:])
    #remove duplicated flags
    ALL['flag']=ALL['flag'].apply(remove_duplicates)
    return ALL


    
#indicatorsFilter is a subset of the indicators to be calcualted in one catalogue  
def catalogueFormulas(catalogue_name, indicatorsFilter=[], isExcel=False, excelSheet=""):
    #Obtain files to download    
    #Read catalogue
    if isExcel:
        catalogue=pd.read_excel(root_path_n+catalogue_name, excelSheet, keep_default_na=False)
    else:        
        catalogue=pd.read_csv(root_path_n+catalogue_name, keep_default_na=False)            
    
    #Parameters
    outputFiles=[]
    counter=0  
    outputfile="output_file"
    if "output_file" not in catalogue.columns:
        outputfile="table" 
    engine="formula_engine"
    formulaCode="formula"
    factorsNumber=14
    
    for i in range(len(catalogue)):
        #print(catalogue.columns)
        if ((catalogue.loc[i][outputfile].strip() in indicatorsFilter) or (len(indicatorsFilter)==0)) and catalogue.loc[i][engine].strip()=='Y':
            counter+=1
            print('Calculating.....'+str(counter)+":"+str(catalogue.loc[i]["IND_CODE"]).strip()) 
            #catalogue.loc[i][at].strip()
            outputFile=catalogue.loc[i][outputfile].strip()
            outputFiles.append(outputFile)
            formula=catalogue.loc[i][formulaCode].strip()
            factors=[]
            for fact in range(factorsNumber):  
                factor_nr="factor"+str(fact+1)                
                if catalogue.loc[i][factor_nr].strip()!="":
                    factors.append(eval(catalogue.loc[i][factor_nr].strip().replace(' ','')))           
            
            
            myResult=calculateIndicator(formula,factors)                    
            myResult['file']=outputFile
            #To clean possible errors 
            #print(myResult[myResult.value_n==-np.inf]) 
            myResult=myResult.replace([np.inf, -np.inf], np.nan)
            myResult.to_csv(calculated_path+outputFile+'.csv',index=False, float_format='%.3f')      
     
                                
    #Check if there are duplicate names in the catalogue
    if len(set(outputFiles)) > len(outputFiles):
        print("WARNING: File names duplicated")
        print(set([x for x in a if outputFiles.count(x) >= 2]))        
    

    

