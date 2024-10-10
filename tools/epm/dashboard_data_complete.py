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
EUCountries=["EU27_2020","EA20","BE","BG","CZ","DK","DE","EE", "IE", "EL", "ES", "FR", "HR", "IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE"]
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
estatSignificances=pd.read_csv(reports_path_n + "EPM Dashboard\\config\\EPM_significances2021.csv")

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

data=data[data.geo.isin(EUCountries)]
AllData=data.copy()

#loop per indicator
dashboard=pd.DataFrame()
indicators=data.groupby(by=['IndicatorID'])
refYear=""
dashboardData={}
for nme, gr in indicators:
    myIndicator=nme[0] ############ <––-–
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

#HERE IT'S WHERE THE CREATE EXCEL DASHBOARD PROGRAMME STARTS

import xlsxwriter

 # Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook(reports_path_n + "\\EPM Dashboard\\EPM_dashboard_2022_Aug.xlsx")
worksheet = workbook.add_worksheet()

#Formats
bold = workbook.add_format({'bold': True})
basic = workbook.add_format({'bold': True, 'align':'center', 'border':1})
st_indicator_name = workbook.add_format({'bold': True, 'align':'center', 'border':1, 'font_size':14, 'font_color':'#4F81BD'})
st_group = workbook.add_format({'bold': True,  'align':'center', 'valign':'vcenter', 'border':1, 'rotation':90,'text_wrap':True})
st_country = workbook.add_format({'font_color':'#FFFFFF', 'bg_color': '#1F497D', 'bold': True, 'align':'center', 'valign':'vcenter','border':1})
#Format for the background colours and significance
positive = workbook.add_format({'bg_color': '#C4D79B','align':'center', 'border':1})
negative = workbook.add_format({'bg_color': '#DA9694','align':'center', 'border':1})
no = workbook.add_format({'bold': True, 'align':'center','border':1})

def colAuto(start=0,step=1):
    i=start
    while 1:
        yield i
        i+=step

#General layout
worksheet.set_column(1, 1, 25)
worksheet.set_row(1, 30)

# Start from the first cell below the headers.
row = 1
#Iterator for columns, to reset per line
dynCol = colAuto()
indic=0

# Iterate over the dictionary of data using the order number as parameter
while indic < len(dashboardData): 
    #print(indic)
    indic+=1    
    #assure that the order exists because of removing and adding orders
    if indic in dashboardData:        
        #Countries row
        if indic==1 or indic==10:
            dynCol = colAuto()
            worksheet.write(row, next(dynCol),     "", basic) 
            worksheet.write(row, next(dynCol),     "", st_country) 
            for country in EUCountries:
                worksheet.write(row, next(dynCol), country, st_country)  
            row += 1        
        
        ID, label, refYear, change, data=dashboardData[indic]        
        #Indicator name
        
        worksheet.merge_range(row, 1,row, len(EUCountries)+1, label, st_indicator_name)        
        row += 1    
         
        rowLabels=[refYear, str(refYear-1)+"-"+str(refYear)+" change in "+ change, str(refYear-3)+"-"+str(refYear)+" change in "+ change ]    
        for subRow in range(len(rowLabels)):
            #print(str(rowLabels[subRow]))
            # 2 Empty column
            dynCol = colAuto()            
            next(dynCol)
               
            worksheet.write(row, next(dynCol) ,str(rowLabels[subRow]), basic)
            for country in EUCountries:                
                if (country,) in data:
                    mydata=data[(country,)]
                    #We have three elements, one per row, and per element two positions: [value, style]
                    rowValues=[[str(mydata[0]), basic],[str(mydata[2]),eval(mydata[4])],[str(mydata[5]),eval(mydata[7])]]
                    #print(rowValues)                    
                    worksheet.write(row,next(dynCol) ,rowValues[subRow][0], rowValues[subRow][1])  
                else:
                    worksheet.write(row,next(dynCol),"n.a.", basic)
            row+=1
    
dynCol = colAuto()
worksheet.write(row, next(dynCol),     "", basic) 
worksheet.write(row, next(dynCol),     "", st_country) 
for country in EUCountries:
    worksheet.write(row, next(dynCol), country, st_country)  



#Summary
summary = workbook.add_worksheet()
summary.set_column(0, 0, 80)
summary.set_column(1,7, 15)

dynCol = colAuto()    
summary.write(0,next(dynCol) ,"indicator" , st_country)

summary.write(0,next(dynCol) ,"Short Positive_Flag" , st_country)
summary.write(0,next(dynCol) ,"Short Negative_Flag" , st_country)
summary.write(0,next(dynCol) ,"Long Positive_Flag" , st_country)
summary.write(0,next(dynCol) ,"Long Negative_Flag" , st_country)


row = 1
#Iterator for columns, to reset per line
indic=0

while indic < len(dashboardData): 
    indic+=1
    if indic in dashboardData:
        dynCol = colAuto()
        ID, label, refYear, change, data=dashboardData[indic]   
        summary.write(row,next(dynCol) ,label, basic)
        short_positive_flags=0
        short_negative_flags=0
        long_positive_flags=0
        long_negative_flags=0
        #Count flags
        for key, value in data.items():
            #Exclude aggregates from the count
            if len(key)==2:
                if value[4]=='positive':
                    short_positive_flags+=1
                if value[4]=='negative':
                    short_negative_flags+=1
                if value[7]=='positive':
                    long_positive_flags+=1
                if value[7]=='negative':
                    long_negative_flags+=1
        summary.write(row,next(dynCol) ,short_positive_flags, basic)
        summary.write(row,next(dynCol) ,(-1)*short_negative_flags, basic)
        summary.write(row,next(dynCol) ,long_positive_flags, basic)
        summary.write(row,next(dynCol) ,(-1)*long_negative_flags, basic)
        
    row += 1



#reporting
reporting = workbook.add_worksheet()
dynCol = colAuto()    
reporting.write(0,next(dynCol) ,"indicator" , st_country)
reporting.write(0,next(dynCol) ,"Country" , st_country)
reporting.write(0,next(dynCol) ,"ref year" , st_country)
reporting.write(0,next(dynCol) ,"Value" , st_country)
reporting.write(0,next(dynCol) ,"flag" , st_country)
reporting.write(0,next(dynCol) ,"short_chg" , st_country)
reporting.write(0,next(dynCol) ,"short_flag" , st_country)
reporting.write(0,next(dynCol) ,"long_chg" , st_country)
reporting.write(0,next(dynCol) ,"long_flag" , st_country)

row = 1
#Iterator for columns, to reset per line
indic=0
reporting.set_column(0, 0, 75)
# Iterate over the dictionary of data using the order number as parameter
while indic < len(dashboardData): 
    indic+=1
    if indic in dashboardData:
        ID, label, refYear, change, data=dashboardData[indic]   
        for country in EUCountries:
            if country in data:
                mydata=data[country]     
                if str(mydata[1])!='' or  str(mydata[3])!='' or  str(mydata[6])!='':
                    dynCol = colAuto()            
                    reporting.write(row,next(dynCol) ,label, basic)
                    reporting.write(row,next(dynCol) ,country, basic)
                    reporting.write(row,next(dynCol) ,refYear, basic)
                    for number in range(8):
                        if number not in [4,7]:
                            reporting.write(row,next(dynCol) ,str(mydata[number]), basic)
                    row += 1




workbook.close()
