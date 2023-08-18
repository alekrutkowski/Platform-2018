# -*- coding: utf-8 -*-
"""
Created on Mon Jul  7 13:59:29 2014
This module represents a catalogue object and childrens

@author: arranda
"""

import csv

from util.download_data import *

#Data is the Dataframe, dimension is the dimension with different values to obtain the priority, order is the priority order
def getDataByPriority(df, dimension, sorter):      
    #Get all the year-geo combination
    dates=pd.DataFrame(df, columns=['geo','year'])
    dates=dates.drop_duplicates()
    #filter to have only the dimensions in the sorter
    df=df[df[dimension].isin(sorter)]
    
    # Define the dimension as a category supporting specific order
    df[dimension] = df[dimension].astype("category")
    df[dimension].cat.set_categories(sorter, inplace=True)
    df=df.dropna(subset=['value_n']).sort([dimension]).groupby(['geo','year']).first()
    df=df.reset_index()
    
    # Join the data with the combination of year-geo to don't miss any records because lack of data
    final=pd.merge(dates,df, on=['geo','year'], how='outer')
    return final


class catalogue:
    #codes to find in the catalogue
#    indID="IND_CODE"
#    indTable="table"
#    indConditions="cond"
#    indStandard="standard"
#    conditionsNumber=5
    attributes=["IND_CODE","table","standard"]
    conditions=["cond1","cond2","cond3","cond4","cond5","cond6","cond7","cond8","cond9","cond10"]
    error_messages=[]
    
    #data cache to increase performance
    dataCache=[False,False]    
        
    def __init__(self, catalogueName, isExcel=False, excelSheet=""):
        self.catalogueName=catalogueName        
        indicators=[]    
        error_messages=[]
        
        #Read catalogue
        if isExcel:
            catalogue=pd.read_excel(root_path_n+catalogueName, excelSheet, keep_default_na=False)
        else:        
            catalogue=pd.read_csv(root_path_n+catalogueName)            
        
        self.catalogue=catalogue        
        
        #Counts how many conditions are there in the catalogue
        nrCond=0
        for c in self.conditions:
            if c in catalogue.columns:
                nrCond=nrCond+1 
        self.conditions=self.conditions[:nrCond] # Truncates to the actual number of conditions (dimensions)       
        print('This catalogue has '+str(nrCond)+' conditions(dimensions).')
       
        catalogue=catalogue.replace(np.nan,"")        
        catalogue['IND_CODE']=catalogue['IND_CODE'].map(str)
        for i in range(len(catalogue)):
            myIndicator=[]
            cond=[]
            for at in self.attributes:               
                myIndicator.append(catalogue.loc[i][at].strip())
            for c in self.conditions:
                cond.append(catalogue.loc[i][c].strip())
            myIndicator.append(cond)    
            indicators.append(myIndicator)                    
        
        self.indicators=indicators       
      
        #TODO: Check that there are no duplicates in the catalogue
        #for check in ['IND_CODE', 'Indicator']:        
        for check in ['IND_CODE']:  
            checks=catalogue.duplicated([check])            
            if len(checks[checks==True])>0:
                raise Exception("ERROR: Duplicated "+check+" :"+str(list(catalogue[check][catalogue.index.isin(list(checks[checks==True].index))])))  
  
        
    def getIndicatorData(self,indicatorID):
        myIndicator=[x for x in self.indicators if x[0] == indicatorID][0] 
        print(myIndicator)
        isStandard=myIndicator[2]
        dataTable=myIndicator[1] 
        #print(dataTable+"--"+isStandard)
        if dataTable=="":
             print("ERROR: Not table defined:"+indicatorID)
             return
        
        #Get data
        data=pd.DataFrame() 
        try:
            if self.dataCache[0] == dataTable:
                data=self.dataCache[1]
            elif isStandard=='Y':
                mess=download_and_stack([dataTable])
                if mess !="":           
                    self.error_messages.append(mess)            
                data=pd.read_csv(stacked_path+dataTable+'.csv')                  
            elif isStandard=='N':
                data=pd.read_csv(calculated_path+dataTable+'.csv')
            else:  
                #self.error_messages.append("ERROR: Standard or not not defined for:"+indicatorID)
                raise Exception("ERROR: Standard or not not defined for:"+indicatorID)        
            self.dataCache=[dataTable,data]
        except Exception as e:
            self.error_messages.append("ERROR: Reading file for:"+indicatorID+" --- "+ str(e))
            print("ERROR: Reading file for:"+indicatorID+" --- "+ str(e))            
            return
        
        try:
            #Filter data dimensions
            indicatorData=data.copy()
            #aproximatin to the data dimensions (all the dimensions - year, geo, file, value, value_n, flag)
            aproxDimensions=len(indicatorData.columns)-6
            
            dimensions= [x for x in myIndicator[3] if x != ""]
            
            #Maybe this will not work with non-standard files
            if (len(dimensions)<aproxDimensions):
                print("WARNING --- Maybe dimensions missing")
            
            for i in range(len(dimensions)):
                dim=(dimensions[i].split('=')[0]).strip()           
                val=(dimensions[i].split('=')[1]).strip()
                indicatorData[dim]=indicatorData[dim].astype(str) 
                #Conditional values, if the vlaue of the dimension contains ||
                # Per country we select the values in the right order to assure completiness of series
                # WARNING: THe conditional dimension must be the last one, only one per indicator
                if "||" in val:
                    print(dim)
                    print(val.split("||"))
                    indicatorData=getDataByPriority(indicatorData,dim,val.split("||"))                
                else:                      
                    indicatorData=indicatorData[(indicatorData[dim]==val)]
                    #Check that the data are correct: unique values and not null
                    if len(indicatorData)==0:
                        print("ERROR --- No data for this indicator after filter by:"+dim+"="+val)                    
            
            indicatorData['IndicatorID']=indicatorID                  
        
            if max(indicatorData.groupby(['geo','year']).size())>1:
                self.error_messages.append("TOO MUCH VALUES. Dimensions bad defined for:"+indicatorID)
                print("TOO MUCH VALUES. Dimensions bad defined for:"+indicatorID)
                #raise Exception("TOO MUCH VALUES. Dimensions bad defined for:"+indicatorID)
        except Exception as e:
            self.error_messages.append("ERROR: "+indicatorID+" --- "+ str(e))
            print("ERROR:"+indicatorID+" --- "+ str(e))            
            
        return indicatorData        
        
    
    def getAllData(self):        
         # Sort by filename to increase performance
         sortedIndicators=sorted(self.indicators, key=lambda indicator: indicator[1])
         final=pd.DataFrame()
         for ind in sortedIndicators:
             temp=self.getIndicatorData(ind[0])
             if final.empty and temp is not None:
                 final=temp.copy()
             else:  
                 final=pd.concat([final, temp], ignore_index=True) # final=final.append(temp) # https://stackoverflow.com/a/75956237
         #Compilation of blocking errors
         if len(self.error_messages)>0:  
             print("============")
             for msg in self.error_messages:
                 print(msg)
             raise Exception("CRITICAL ERRORS ABOVE")
            
         return final  
         
    #To obtain specific information added to the catalogue
    def getSpecialField(self,fieldName):      
        #Get catalogue
        specialField=[]
        for i in range(len(self.catalogue)):
            specialField.append([self.catalogue.loc[i]["IND_CODE"],self.catalogue.loc[i][fieldName]])         
        return dict(specialField)       
            
        
#cat_radar=catalogue('RADAR - catalogue.csv')