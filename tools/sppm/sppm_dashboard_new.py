# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 09:28:44 2015

@author: arranda
"""
from formula_engine.engine_v2 import *
from util.tools import * 
from util.catalogues import *
from tools.sppm.substantive import *
from tools.sppm.sppm_config import *

startYear=2019
EUCountries=["EU27_2020", "EU27_2007", "EA18", "EA19", "BE", "BG", "CZ", "DK", "DE", "EE", "IE", "EL", "ES", "FR", "HR", "IT", "CY", "LV", "LT", "LU", "HU", "MT", "NL", "AT", "PL", "PT", "RO", "SI", "SK", "FI", "SE"]

#Get data and read configuration
def getDashboardData(catalogue_object, cat_non_standard, file_output):    
    catalogueFormulas(cat_non_standard)   
    mergedFile=catalogue_object.getAllData()
    mergedFile=pd.DataFrame(mergedFile,columns=['IndicatorID','geo','year','values','value_n','flag','file'])    
    mergedFile['value_n']=pd.to_numeric(mergedFile['value_n'])
    mergedFile.to_csv(merged_path+file_output+'.csv',index=False, float_format='%.2f')
    return mergedFile
 
#typeOfChange pp or %
#changeDistance short or long
#indicatorData is a df with all the data for that country and that indicator
def getChange(typeOfChange, final_value, original_value, decimals, country, changeDistance,indicatorCountryData,myIndicator):   
        
    #Manage exceptions
    #TODO: Clean everyyear
    #Exceptions for ref Year
    isSILCindicator=isSILC[myIndicator]

#    if changeDistance=='long' and country=='BG' and myIndicator in ['ID2','ID3','ID4','ID19']:          
#        final_value=float(indicatorCountryData['value_n'][indicatorCountryData.year==2013])
#    if changeDistance=='long' and country=='HR' and isSILCindicator=='Y':
#        original_value=float(indicatorCountryData['value_n'][indicatorCountryData.year==2010])
#    if changeDistance=='long' and country=='LU' and isSILCindicator=='Y':          
#        final_value=float(indicatorCountryData['value_n'][indicatorCountryData.year==2015])
#    if changeDistance=='long' and country=='AT' and myIndicator in ['ID24']:          
    #     return "n.a."
    
    # if changeDistance=='short' and country=='BE' and isSILCindicator=='Y':          
    #     return "n.a."
    
    # if changeDistance=='long' and country=='BE' and isSILCindicator=='Y':          
    #     final_value=float(indicatorCountryData['value_n'][indicatorCountryData.year==2018])
    
    # if changeDistance=='long' and country=='BE' and myIndicator in ['ID18']:          
    #     return "n.a."
    
    # if changeDistance=='long' and country=='EE' and isSILCindicator=='Y':          
    #     return "n.a."
        
    # if changeDistance=='long' and country=='HR' and isSILCindicator=='Y':
    #     original_value=float(indicatorCountryData['value_n'][indicatorCountryData.year==2010])

    # if changeDistance=='long' and country=='RO' and myIndicator in ['ID14','ID8','ID21','ID15','ID9']:
    #     original_value=float(indicatorCountryData['value_n'][indicatorCountryData.year==2010])

    # if changeDistance=='long' and country=='SI' and myIndicator in ['ID18','ID23','ID22']:        
    #     return "n.a."
        
    # Issues with the EU28 GDHI aggregate short and long
    #   if country=='EU28' and myIndicator in ['ID26']:          
    #      return "n.a."    
      
    myChange="n.a."
    if typeOfChange=="pp":
        myChange=round(final_value-original_value,decimals)
    elif typeOfChange=="%":
        myChange=round(100*(final_value-original_value)/original_value,decimals)
        # Here maybe exception?    
    else:
        raise Exception("Type of change not defined")  
    
    if np.isnan(myChange):
        myChange='n.a.'
    return myChange
        
def getFlagChange(listOfFlags):
    return ''.join(set(''.join(listOfFlags)))
    

# Combine per indicator, country, indicator levels of significance (either from config or from ESTAT)
# with levels of sustantiveness (from config) and choose the higher value to check against the data 
def getSignificance_Sustantiveness(indicator, country, typeOfChange, senseOfChange, changeLength, value):
    if value=="n.a.":
        return "no"
        
    mySignificance=""
    #get significance and sustantiveness and choose the biggest one
    if changeLength=="short":
        mySignificance=np.nanmax([significance_short[indicator], substantiveness_short[indicator]])
    elif changeLength=="long":
        mySignificance=np.nanmax([significance_long[indicator], substantiveness_long[indicator]])
        
    significance_ESTAT= estatSignificances[changeLength][(estatSignificances.IndicatorID==indicator) & (estatSignificances.geo==country)]
    if len(significance_ESTAT)>0:
        mySignificance=np.nanmax([mySignificance,significance_ESTAT.iloc[0]])
     
    if abs(value)> mySignificance:
        if (senseOfChange=="pos" and value>0) or (senseOfChange=="neg" and value<0):
            return "positive"
        else:
            return "negative"
    return "no"

def calculateAROPthreshold():
    download_and_stack(['ilc_li01','prc_hicp_aind'])
    for child in ['A1','A2_2CH_LT14']:
        ilc_li01=pd.read_csv(stacked_path+'ilc_li01.csv')
        #IN principle we use NAC to claculate the change but there are countries with broken series due to the transition to Euro
        # we need to combine the two groups in a single one
        ilc_li01_a=ilc_li01[(~ilc_li01.geo.isin(['CY','SK','LT']))&(ilc_li01.currency=='NAC')&(ilc_li01.hhtyp==child)&(ilc_li01.indic_il=='LI_C_MD60')]
        ilc_li01_b=ilc_li01[(ilc_li01.geo.isin(['CY','SK','LT']))&(ilc_li01.currency=='EUR')&(ilc_li01.hhtyp==child)&(ilc_li01.indic_il=='LI_C_MD60')]
        ilc_li01_final=ilc_li01_a.append(ilc_li01_b)
        
        prc_hicp_aind=pd.read_csv(stacked_path+'prc_hicp_aind.csv')
        prc_hicp_aind=prc_hicp_aind[(prc_hicp_aind.coicop=='CP00')&(prc_hicp_aind.unit=='INX_A_AVG')]
        #Decalate 1 year to deflate the income year of SILC
        prc_hicp_aind['year']=prc_hicp_aind['year']+1
        
        merged=pd.merge(ilc_li01_final, prc_hicp_aind, on=['geo','year'])
        merged['value_n']=100*merged['value_n_x']/merged['value_n_y']
        merged.to_csv(calculated_path+'real_pov_threshold_'+child+'.csv')
        
  
#Main thread
#Read configuration

myCatalogue=catalogue(myCatalogue_name) #the object catalogue
#estatSignificances=pd.read_csv(reports_path_n + 'SPPM Dashboard/config/significances2020.csv')  
#Calculate indicators before running the catalogue   
calculateAROPthreshold()
#Run GDHI programme

#get data: Either new data from ESTAT (run catalogue) or last version ran
data=getDashboardData(myCatalogue, myCatalogue_name, dashboard_merged) #New data from ESTAT
#data=pd.read_csv(merged_path+'SPPM_dashboard.csv') # acces to last version of data

#Calculate substantiveness thresholds
getSubstantive('SPPM') # This function is located in program substantive.py

#Reload and read configuration because the substantivenness have just been calculated
myCatalogue=catalogue(myCatalogue_name)
sense=myCatalogue.getSpecialField("sense")    
changeType=myCatalogue.getSpecialField("change")
order=myCatalogue.getSpecialField("Order")
decimals=myCatalogue.getSpecialField("decimals")
description=myCatalogue.getSpecialField("Indicator")
significance_short=myCatalogue.getSpecialField("significance_short")
significance_long=myCatalogue.getSpecialField("significance_long")
substantiveness_short=myCatalogue.getSpecialField("substantiveness_short")
substantiveness_long=myCatalogue.getSpecialField("substantiveness_long")
isSILC=myCatalogue.getSpecialField("is_SILC_indicator")

#Filter data
data=data[data.geo.isin(EUCountries)]
#Copy of the data for the counttry profiles
AllData=data.copy()

#loop per indicator
dashboard=pd.DataFrame()
indicators=data.groupby(by=['IndicatorID'])
refYear=""
#Dictionary that will keep the data to create the dashbaord
#The key will be the number of the order configured in the catalogue
dashboardData={}
#loop per indicator
for name, group in indicators: # Here name is the name of a group so the loop is on one index only
    myIndicator=name
    #Indicator configuration
    type_of_change=changeType[myIndicator] # changeType is a vector and acces is toward myIndicator
    type_of_sense=sense[myIndicator]
    number_of_dec=decimals[myIndicator]
    
    indicatorData=pd.DataFrame(group) # Here all data for a specific indicator
    #Find reference year for the indicator
    if len(indicatorData[(indicatorData.value_n.notnull()) & (indicatorData.year==max(indicatorData['year']))])>12: #Here 20 is hard coded
        refYear=max(indicatorData['year'])
    else:
        refYear=max(indicatorData['year'])-1
    #if (name=='ID19'): refYear=2019
    
    #use this for pseudo-dashboard with latest data only
    #refYear=2020
    
    #mydata is an array that contains all the metainformation and country data per indicator
    myData=[myIndicator,description[myIndicator], refYear, type_of_change]
    #This structure contins the detail of the data per country
    dictDataIndicators={}
        
    indCountryData=indicatorData.groupby(by=['geo'])
    #Loop per country
    for name, group in indCountryData:
        #startYear==2019
        country=name            
        refValue =  refFlag = short_flag =  long_flag = extraFlag = ""        
        short_change  = long_change ="n.a."
        significanceShort = significanceLong = "no"      
        
        
        #Find the right value for level, either reference year or one year before and the corresponding flag
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
                short_change=getChange(type_of_change,float(refValue),float(group['value_n'][group.year==(refYear-1)]),1, country, 'short',group,myIndicator)
                short_flag=getFlagChange(list(group['flag'][(group.year.isin([refYear,(refYear-1)])) & (group.flag.notnull())]))
                significanceShort=getSignificance_Sustantiveness(myIndicator,country,type_of_change,type_of_sense, "short", short_change)
                
            #Long
            if len(group[(group.year==startYear) & (group.value_n.notnull())])==1:            
                long_change=getChange(type_of_change,float(refValue),float(group['value_n'][group.year==startYear]),1, country, 'long',group,myIndicator)
                long_flag=getFlagChange(list(group['flag'][(group.year<refYear)&(group.flag.notnull())]))+extraFlag
                significanceLong=getSignificance_Sustantiveness(myIndicator,country,type_of_change,type_of_sense, "long", long_change)
                
        #TODO: Exceptional cases to be treated
        #decimals
        if refValue!="":
            formatter="{:."+str(number_of_dec)+"f}"
            refValue=formatter.format(refValue)
        else:
            refValue="n.a."
  
        #Cosmetic changes to hide results not flagged
#        if significanceShort=="no" and refValue!="n.a." and short_change!="n.a.":
#            short_change="~"
#        if significanceLong=="no"  and refValue!="n.a." and long_change!="n.a.":
#            long_change="~"
            
        #Output      
        dictDataIndicators[country]=[refValue,refFlag,short_change,short_flag,significanceShort,long_change,long_flag, significanceLong]
    myData.append(dictDataIndicators)
    dashboardData[order[myIndicator]]=myData
    
    #print(dashboardData)
    #break

#Exceptions
    
#Remove the dashboard values for the second GDHI value '27'
dashboardData.pop(29)
#Replace values in alldata for ID26 by ID27 for the country profile
# GDHI growth has to be shown in different ways
AllData=AllData[AllData.IndicatorID!='ID26']
AllData=AllData.replace("ID27","ID26")
AllData.loc[AllData.IndicatorID=="ID26", 'value_n']=AllData['value_n'][AllData.IndicatorID=="ID26"].round(1)

#At poverty threshold use the changes in currencies and replace the levels by the PPS indicator
# In all data remove the data for threshold in national currencies
#IN this case member is a country 
for member in dashboardData[30][4]:
    dashboardData[3][4][member][0]=dashboardData[30][4][member][0] #replace level
    dashboardData[3][4][member][1]=dashboardData[30][4][member][1] #replace level flag
  
#This will be used as extra information in the dashboard
threshold_PPS=dashboardData[30][4]
# remove threshold in PPS from the data to be used in the dashboard
dashboardData.pop(30)

#For the country profile of the dashboard
#For the time series in we replace the NAC indicator by the PPS
AllData=AllData[AllData.IndicatorID!='ID7']
AllData=AllData.replace("ID28","ID7")




#-----------------------------
#here the create_dashboard programme starts

import xlsxwriter

#from config.parameters import *
#from tools.sppm.sppm_dashboard import order

 # Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook(reports_path_n + "SPPM Dashboard/" + dashboard_final_file)
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
#groups
worksheet.merge_range(2, 0, 21, 0, '2030 target', st_group)
worksheet.merge_range(22, 0,25, 0, 'Intensity of poverty risk', st_group)
worksheet.merge_range(26, 0,29, 0, 'Persistence of poverty risk', st_group)
worksheet.merge_range(30, 0,33, 0, 'Income inequalities', st_group)
worksheet.merge_range(34, 0,45, 0, 'Child poverty and social exclusion', st_group)
worksheet.merge_range(46, 0,53, 0, 'Effectiveness of social protection system', st_group)
worksheet.merge_range(54, 0,61, 0, 'Social consequences of labour market', st_group)
#break
worksheet.merge_range(63, 0,74, 0, 'Youth exclusion', st_group)
worksheet.merge_range(75, 0,78, 0, 'Active ageing', st_group)
worksheet.merge_range(79, 0,90, 0, 'Pension adequacy', st_group)
worksheet.merge_range(91, 0,100, 0, 'Health', st_group)
worksheet.merge_range(101, 0,104, 0, 'Access to decent Housing', st_group)
worksheet.merge_range(105, 0,107, 0, 'Evolution in real household disposable income', st_group)

# Start from the first cell below the headers.
row = 1
#Iterator for columns, to reset per line
dynCol = colAuto()
indic=0

# Iterate over the dictionary of data using the order number as parameter
while indic < len(order): 
    indic+=1
    #Don't display indicator 13 as is not for the dashboard
    if indic==13:
        continue
    #assure that the order exists because of removing indicators
    if indic in dashboardData:        
        #Countries row
        if indic==1 or indic==17:
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
         
        rowLabels=[refYear, str(refYear-1)+"-"+str(refYear)+" change in "+ change, "2019-"+str(refYear)+" change in "+change ]    
        for subRow in range(len(rowLabels)):
            #print(str(rowLabels[subRow]))#Empty column
            dynCol = colAuto()
            #empty column
            next(dynCol)
            #Exceptions in the indicator that are not showing levels (GDHI) or not showing short-term changes (healthy life years)- ONLY GDHI UNTIL 2021 DATA ARE AVAILABLE           
            if (ID in ['ID26'] and rowLabels[subRow]==rowLabels[0]): #or (ID  in ['ID22','ID23'] and rowLabels[subRow]==rowLabels[1]) or (ID  in ['ID29'] and rowLabels[subRow]==rowLabels[2]):
                print("no row "+ID+" "+str(rowLabels[subRow]) )
            else:
                worksheet.write(row, next(dynCol) ,str(rowLabels[subRow]), basic)
                for country in EUCountries:                
                    if country in data:
                        mydata=data[country]
                        #We have three elements, one per row, and per element two positions: [value, style]
                        rowValues=[[str(mydata[0]), basic],[str(mydata[2]),eval(mydata[4])],[str(mydata[5]),eval(mydata[7])]]                    
                        worksheet.write(row,next(dynCol) ,rowValues[subRow][0], rowValues[subRow][1])  
                    else:
                        worksheet.write(row,next(dynCol),"n.a.", basic)
                row+=1
   
#final column with the names of the countries    
dynCol = colAuto()
worksheet.write(row, next(dynCol),     "", basic) 
worksheet.write(row, next(dynCol),     "", st_country) 
for country in EUCountries:
    worksheet.write(row, next(dynCol), country, st_country)  


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

#Poverty threshold in PPS
poverty = workbook.add_worksheet()
dynCol = colAuto() 
poverty.write(0,next(dynCol) ,"Country" , st_country)
poverty.write(0,next(dynCol) ,"Value" , st_country)
poverty.write(0,next(dynCol) ,"flag" , st_country)
poverty.write(0,next(dynCol) ,"short_chg" , st_country)
poverty.write(0,next(dynCol) ,"short_flag" , st_country)
poverty.write(0,next(dynCol) ,"short_significance" , st_country)
poverty.write(0,next(dynCol) ,"long_chg" , st_country)
poverty.write(0,next(dynCol) ,"long_flag" , st_country)
poverty.write(0,next(dynCol) ,"long_significance" , st_country)
row = 1
for member in threshold_PPS:
    dynCol = colAuto() 
    poverty.write(row,next(dynCol), member, basic)
    for element in threshold_PPS[member]:        
        poverty.write(row,next(dynCol), element, basic)
    row += 1


workbook.close()

#----------
#START OF THE CREATE COUNTRY PROFILES

import xlsxwriter

 # Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook(reports_path_n + 'SPPM Dashboard/' + country_profile_final_file)
columnYears=[2019,2020,2021]
#myCountry="UK"

def formatChange(myChange, typeOfChange):
    if myChange not in ['~', 'n.a.' ]:
        return myChange+" "+typeOfChange
    else:
        return myChange

def colAuto(start=0,step=1):
    i=start
    while 1:
        yield i
        i+=step

#Formats
bold = workbook.add_format({'bold': True})
basic = workbook.add_format({'align':'center','valign':'vcenter', 'border':1})
st_indicator_name = workbook.add_format({'bold': True, 'align':'center', 'border':1, 'font_size':11, 'text_wrap':True})
st_group = workbook.add_format({'bold': True,  'align':'center', 'valign':'vcenter', 'border':1,'text_wrap':True})
st_country = workbook.add_format({'font_color':'#FFFFFF','text_wrap':True, 'bg_color': '#1F497D', 'bold': True, 'align':'center', 'valign':'vcenter','border':1})
#Format for the background colours and significance
positive = workbook.add_format({'bg_color': '#C4D79B','align':'center','valign':'vcenter', 'border':1})
negative = workbook.add_format({'bg_color': '#DA9694','align':'center','valign':'vcenter', 'border':1})
no = workbook.add_format({'align':'center','valign':'vcenter','border':1})

for myCountry in EUCountries:
    print(myCountry)
    worksheet = workbook.add_worksheet(myCountry)
    #General layout
    worksheet.set_column(0, 0, 23)
    worksheet.set_column(1, 1, 30)
    worksheet.merge_range(1, 2, 1, 6, myCountry, st_group)
    worksheet.merge_range(1, 8, 1, 10, "EU27_2020", st_group)
    
    #groups
    worksheet.merge_range(3, 0, 7, 0, '2030 target', st_group)
    worksheet.write(8, 0, 'Intensity of poverty risk', st_group)
    worksheet.write(9, 0, 'Persistence of poverty risk', st_group)
    worksheet.write(10, 0,'Income inequalities', st_group)
    worksheet.merge_range(11, 0, 13, 0, 'Child poverty and social exclusion', st_group)
    worksheet.merge_range(14, 0,16, 0, 'Effectiveness of social protection system', st_group)
    worksheet.merge_range(17, 0,18, 0, 'Social consequences of labour market', st_group)
    worksheet.merge_range(19, 0,21, 0, 'Youth exclusion', st_group)
    worksheet.write(22, 0,'Active ageing', st_group)
    worksheet.merge_range(23, 0,25, 0, 'Pension adequacy', st_group)
    worksheet.merge_range(26, 0,28, 0, 'Health', st_group)
    worksheet.write(29, 0, 'Access to decent housing', st_group)
    worksheet.write(30, 0, 'Evolution in real household disposable income', st_group)
    
    # Start from the first cell below the headers.
    row = 2
    #Iterator for columns, to reset per line
    dynCol = colAuto()
    indic=0
    
    #headers
    worksheet.write(row, next(dynCol),     "Group", st_country) 
    worksheet.write(row, next(dynCol),     "Indicator", st_country) 
    for myYear in columnYears:
        worksheet.write(row, next(dynCol),     str(myYear), st_country) 
    worksheet.write(row, next(dynCol),     "latest year change", st_country) 
    worksheet.write(row, next(dynCol),     "change 2019 to latest year", st_country) 
     #empty column
    next(dynCol)  
    worksheet.write(row, next(dynCol),     "2021", st_country) 
    worksheet.write(row, next(dynCol),     "latest year change", st_country) 
    worksheet.write(row, next(dynCol),     "change 2019 to latest year", st_country) 
    row += 1     
    
    # Iterate over the dictionary of data using the order number as parameter
    for indic in sorted(dashboardData.keys()):      
        ID, label, refYear, change, detailDashboard=dashboardData[indic]        
        #Indicator name
        dynCol = colAuto()
        #empty column
        next(dynCol)  
        worksheet.write(row, next(dynCol),    label, st_indicator_name)
        
        #Levels per year, from full dataset  "AllData"
        number_of_dec=decimals[ID]
        for myYear in columnYears:
            try:
                myData=AllData[(AllData.IndicatorID==ID) & (AllData.geo==myCountry) & (AllData.year==myYear) & (AllData.value_n.notnull())].iloc[0]['value_n']
            except:
                myData="n.a."
            if myData!="" and myData!="n.a.":
                formatter="{:."+str(number_of_dec)+"f}"
                myData=formatter.format(myData)       
            worksheet.write(row, next(dynCol),  myData   , basic) 
        
        #Country Changes
        if myCountry in detailDashboard:
            myChanges=detailDashboard[myCountry]
            worksheet.write(row,next(dynCol) ,formatChange(str(myChanges[2]),changeType[ID]), eval(myChanges[4]))
            worksheet.write(row,next(dynCol) ,formatChange(str(myChanges[5]),changeType[ID]), eval(myChanges[7]))
        else:
            worksheet.write(row,next(dynCol) ,"n.a.", no)
            worksheet.write(row,next(dynCol) ,"n.a.", no)         
            
        #EU Level and changes  
        #empty column
        next(dynCol)
        try:
            myData=AllData[(AllData.IndicatorID==ID) & (AllData.geo=="EU27_2020") & (AllData.year==2021)& (AllData.value_n.notnull())].iloc[0]['value_n']
        except:
            myData="n.a."
        worksheet.write(row, next(dynCol),  myData   , basic)
        
        if "EU27_2020" in detailDashboard:
            myChanges=detailDashboard["EU27_2020"]
            worksheet.write(row,next(dynCol) ,formatChange(str(myChanges[2]),changeType[ID]), eval(myChanges[4]))
            worksheet.write(row,next(dynCol) ,formatChange(str(myChanges[5]),changeType[ID]), eval(myChanges[7]))
        else:
            worksheet.write(row,next(dynCol) ,"n.a.", no)
            worksheet.write(row,next(dynCol) ,"n.a.", no)         
           
        row += 1
  
workbook.close()
