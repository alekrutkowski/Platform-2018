# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 10:45:44 2013

@author: arranda
"""
from util.download_data import *


#Prepares the data to operate with them in a column mode using year-geo as index
def data_prep(df, column_to_pivot):
    df['year-geo']=df['year'].map(str)+'--'+df['geo']        
    df=df.pivot(index='year-geo',columns=column_to_pivot, values='value_n')
    df=df.convert_objects(convert_numeric=True)
    return df  
   
#  This function provide as output a clean data frame with only one column as value ready 
#  to operate after filtering the data and with year-geo as index 
#  conditions must be pased in the format ['age=Y15-64','sex=T']
# rename_column to False is useful when operating within the same dataset   
def prep_for_calc(table,conditions,start_year=0,rename_column=True):
    #print(table)
    #print(conditions)
    dataTable=pd.read_csv(stacked_path+table+'.csv')    
    for i in range(len(conditions)):
        cond=conditions[i].split('=')[0]
        val=conditions[i].split('=')[1]
        #transform condition column in strings, to avoid problems when the condition is a number
        dataTable[cond]=dataTable[cond].astype(str)
        dataTable=dataTable[(dataTable[cond] == val)]    
    if start_year!=0:
        dataTable=dataTable[(dataTable.year > start_year)]
    firstColumn=conditions[0].split('=')[0]
    firstValue=conditions[0].split('=')[1]
    if dataTable.empty:
        print("NO DATA AVAILABLE -- REVIEW CONDITIONS FOR:"+table)    
    dataTable=data_prep(dataTable,firstColumn)
    if rename_column:
        dataTable=dataTable.rename(columns={firstValue: 'val_'+table})
    return dataTable
   
def clean_working_df(a):
    a=a.reset_index()
    a['year']=a['year-geo'].str.split('--').str.get(0)      
    a['geo']=a['year-geo'].str.split('--').str.get(1)
    #remove year-geo
    a = a.drop(['year-geo'], axis=1)
    return a

def getQuarter(x):
    value=x['year'].strip().str.replace('-', '', regex=False)
    if value.endswith('01') or value.endswith('02') or value.endswith('03'):
        return "Q1"
    if value.endswith('04') or value.endswith('05') or value.endswith('06'):
        return "Q2"
    if value.endswith('07') or value.endswith('08') or value.endswith('09'):
        return "Q3"
    if value.endswith('10') or value.endswith('11') or value.endswith('12'):
        return "Q4"
 
def filterByYear(df,startYear):
    df['year']=df['year'].map(str)
    df['year'] = df['year'].str.replace('-', '', regex=False)
    df['real_year']=df['year'].apply(lambda x: x[0:4])
    df['real_year']=df['real_year'].map(int)
    df=df[(df.real_year > startYear)]
    df = df.drop(['real_year'], axis=1)
    return df
   

  
# Function to validate data in unit testing
#schema contains and array with the dimensions to test
#values contains and array with the data to filter the data frame, last value must be the value to test
#Example validate(xx,['geo','year','component','indicator'],['AT','2000Q1 ','Gross disposable income','real_ghdi',35377])  
def validate(dataF, schema, test_values):
    dataF=dataF.reset_index()    
    condition=''
    realValue=''
    for i in range(len(test_values)-1):
        if i !=0:
            condition += ' & '        
        condition += "(dataF."+schema[i]+"=='"+test_values[i]+"')"
    
    #print("dataF['value_n']["+condition+"]")
    realValue=eval("dataF['value_n']["+condition+"]")     
       
    
    if len(realValue)>1:
        print("ERROR: Too much values:"+str(test_values))        
    else:
        realValue=realValue.reset_index()
        realValue=realValue['value_n'][0] 
        if 0.98<((realValue/test_values[len(test_values)-1]))<1.02:    
            print("OK")
        else:
            print("NOK:"+str(test_values)+" -- Real value:"+str(realValue))


#Columns must be in the same order
#def saveDWH(data,outputFile):
#    #rename columns to DWH standards    
#    
#    cols=data.columns 
#    data['time']=data['year']           
#    final_cols=['time']
#    final_cols.extend([c for c in cols if c != 'file'and c != 'value_n' and c != 'flag'  and c != 'year'])
#    final_cols.extend(['file', 'value_n', 'flag'])
#    
#    #create df with the columns in the right order
#    d=pd.DataFrame(data,columns=final_cols)
#    #d.to_csv(jaf_path+outputFile+'.1.csv',index=False, na_rep=':', float_format='%.2f')
#    d.to_csv(dwh_path+outputFile+'.csv',index=False, float_format='%.2f')
#    
    
#Outputfile must be saved before in the calculated folder
def saveDWH(outputFile):
    mappingDimension={}  
    
    #read file
    data=pd.read_csv(calculated_path+outputFile+".csv")
    #rename columns to DWH standards   
    #If dimension doesn't exist use EMPL_custom 
    mappingDimension['year']='time'
    
    #ghdi.csv
    mappingDimension['component']='na_item'
    mappingDimension['deflator']='reason'
    #lfse_er_child
    mappingDimension['children']='n_child'
    
    cols=data.columns 
    print("Verify that dimensions exist in the DWH")
    print(cols)
    
    for oldDimension in cols: 
        if oldDimension in mappingDimension:
            newDimension=mappingDimension[oldDimension]
            data[newDimension]=data[oldDimension]
            data=data.drop([oldDimension], axis=1)
            print("Changed: "+oldDimension +" by "+newDimension)
    
    cols=data.columns 
    final_cols=[]
    final_cols.extend([c for c in cols if c != 'file'and c != 'value_n' and c != 'flag'  and c != 'year'])
    final_cols.extend(['file', 'value_n', 'flag'])
    
    #create df with the columns in the right order
    d=pd.DataFrame(data,columns=final_cols)
    #d.to_csv(jaf_path+outputFile+'.1.csv',index=False, na_rep=':', float_format='%.2f')
    d.to_csv(dwh_path+outputFile+'.csv',index=False, float_format='%.2f')   
    return d
    

#xx=saveDWH('lfse_er_child')
    