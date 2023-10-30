# -*- coding: utf-8 -*-
"""
Created on Mon Jul  7 10:26:47 2014

@author: arranda
"""

#from formula_engine.engine import *
from formula_engine.engine_v2 import *
from util.tools import *
from util.catalogues import *
import numpy as np

#Import specific indicators
#from Indicators.ghdi_esa2010 import *
#from indicators.gdhi_2018_new import *

#make this dynamic by linking it to a file. See where it is used and update
#eu28Countries=['EU28','EU27','EA19','BE','BG','CZ','DK','DE','EE','EL','IE','ES','FR','FX','HR','IT','CY','LV','LT','LU','HU','MT','NL','AT','PL','PT','RO','SI','SK','FI','SE','UK']
eu27Countries=['EU27_2020','EA19','BE','BG','CZ','DK','DE','EE','EL','IE','ES','FR','FX','HR','IT','CY','LV','LT','LU','HU','MT','NL','AT','PL','PT','RO','SI','SK','FI','SE']

#As the FR series are shorter we complete replace them by the FX series 
def replace_FX_FR(data):
    filesFX=set(data['file'][data.geo=='FX'])    
    print("Files with FR/FX problem")
    print(filesFX)
    final=data.copy()
    
    for indicator in set(data['IndicatorID'][data.geo=='FX']):
        #print(indicator)        
        #final=final[final.IndicatorID==indicator]  
        
        # At least 5 data points for FR after 2010
        if len(final[((final.IndicatorID==indicator) & (final.geo=='FR') & (~final.value_n.isnull()))])>5:
              print("NO FR changes in indicator:"+indicator)
        #Not for demographic files
        else:
            #print(list(set(final[final.IndicatorID==indicator]['file']))[0])
            final=final[~((final.IndicatorID==indicator) & (final.geo=='FR'))]
            #This works if no FR records for year before 2014
            final.ix[(final.IndicatorID==indicator) & (final.geo=='FX'),'geo']='FR'
            print("FR replaced by FX in indicator:"+indicator)
        
    return final
   

def EuropeanSemester():
    catalogue_non_standard='European Semester.csv'
    catalogue_standard='European Semester.csv'
    outputFile='european_semester'   
    #Run specific calculated indicators for the project
    #readMainCatalogue()    
    #Run formula engine for the project
    catalogueFormulas(catalogue_non_standard)    
    #Run catalogue
    cat_radar=catalogue(catalogue_standard)
    mergedFile=cat_radar.getAllData()
    mergedFile=pd.DataFrame(mergedFile,columns=['IndicatorID','geo','year','values','value_n','flag','file'])
    #Run specific actions in the data file
    #Filter geo
    mergedFile=mergedFile[mergedFile.geo.isin(eu27Countries)]
    #Add Reference year column in the data file for compatibility with old version    
    mergedFile=filterByYear(mergedFile, 1998)
    mergedFile=replace_FX_FR(mergedFile)
    save_sync(mergedFile,outputFile,3) 
    #the table below is used in the "special" tables but it is so far included in the catalogue
    #download_and_stack(['lfsa_ergaed'])
    return mergedFile    



#lite True means that only basic columns will be produced: geo, year, value_n, values, flag, file
def anyCatalogue(cat_standard, file_output, lite=True, FX_FR=False, join_labels=False):    
    cat_non_standard=cat_standard
    if cat_non_standard!='':
        catalogueFormulas(cat_non_standard)    
    myCatalogue=catalogue(cat_standard)
    mergedFile=myCatalogue.getAllData()
    
    if lite:
        mergedFile=pd.DataFrame(mergedFile,columns=['IndicatorID','geo','year','values','value_n','flag','file'])
    
    #FR/FX issue
    if FX_FR:
        mergedFile=replace_FX_FR(mergedFile)
    
    # Provide labels for people not working with pivot tables
    if join_labels:
        cat=pd.read_csv(root_path_n+cat_standard)
        mergedFile=pd.merge(cat[['IND_CODE','order','Indicator',]], mergedFile, left_on=['IND_CODE'], right_on=['IndicatorID'],how='right')
        mergedFile=mergedFile.drop(['IND_CODE'], axis=1)

    if file_output=='quarterly_annex_data':
        mergedFile['year'] = mergedFile['year'].str.replace('-',"") # Excel file "U:\04 Data and tools\Reports\quarterly\Statistical annex quarterly_A.xlsx" doesn't like the new quarterly format with hyphen

    #Run specific actions in the data file   
    save_sync(mergedFile,file_output)
    
    return mergedFile


def save_sync(mergedFile,outputFile, decimal_numbers=2):
    #Save file
    #Force conversion to numeric to avoid problems with last decimal number in non-standard
    mergedFile['value_n']=pd.to_numeric(mergedFile['value_n'])    
    mergedFile.to_csv(merged_path+outputFile+'.csv',index=False, float_format='%.'+str(decimal_numbers)+'f')
    #Sync folders
    #syncFolders(merged_path,merged_path_p) 
    
#Standard and non-standard catalogue are the same
def quick_excel(list_countries, catalogue, output, start_year=2006, myValue='value_n' ):
    data=anyCatalogue(catalogue, catalogue, output, lite=True, FX_FR=True)
    data=pd.DataFrame(data, columns=['IndicatorID', 'geo','year',myValue])
    data=data[data.year>=start_year]
    data=data.pivot_table(index=['IndicatorID', 'geo'],columns='year', values=myValue)    
    data=data.reset_index()
    cat=pd.read_csv(root_path_n+catalogue)
    final=pd.merge(cat[['IND_CODE', 'Indicator']].astype(str), data.astype(str), left_on=['IND_CODE'], right_on=['IndicatorID'],how='right')
    writer=pd.ExcelWriter(merged_path+output+'.xlsx')
    for geo in list_countries:
        myGeo=final[final.geo==geo]
        myGeo.to_excel(writer, sheet_name=geo, index=False)
        myGeo.to_csv(merged_path+'test.csv')
    writer.save
    return final
    
   
def enlargement_yearly():
    localpath ='C:\\Data\\enlargement\\Outputs\\'
    ENLList=['AL','BA','EU28','ME','MK','RS','TR','XK']

    catalogueENL=pd.read_csv(root_path_n+'catalogue - ENLARG_ys.csv')  # open the catalogue into a data frame  
    catalogueENL = catalogueENL.fillna('')                                    # deletes NaNs and fill the gaps 
    ENL=anyCatalogue('catalogue - ENLARG_ys.csv', 'enlargement', lite=True)
    ENL=ENL[ENL.geo.isin(ENLList)]
    ENL.columns=['IND_CODE', 'COUNTRY','YEAR','fl_values','value_n','flag','file']
    ENL = pd.merge(ENL, catalogueENL, on=['IND_CODE'])
    ENL = ENL[['IND_CODE','Category','List','Indicator','Full name indicator','COUNTRY','YEAR','value_n','flag']]
    ENL.to_csv(localpath+'ENL_y.csv')    

 
def quarterly():
    #add line to call formula for GDHI quarterly
    
    finalData=anyCatalogue('quarterly - catalogue.csv', 'quarterly_recurrent', FX_FR=False)
         
    #Files not used directly from catalogue
    download_and_stack(['jvs_q_nace2'])
    
    # 1) Filter years smaller than 2000    
    finalData=filterByYear(finalData, 2007)
    
    finalData['period_type']=finalData['year'].str[5:6].str.replace('-',"")
    finalData['period_type']=np.where(finalData['period_type']!='Q', 'M', 'Q')
    finalData['y']=finalData['year'].str[0:4]
    finalData['q_m']=finalData['year'].str[4:].str.replace('-',"")
    
    save_sync(finalData,'quarterly_recurrent')


#comment-in the lines related to the excels to be extracted

#a=quick_excel(['PL'], 'PL_ad_hoc.csv','PL_ad_hoc')
quarterly()
quarterlyannex=anyCatalogue('Quarterly Annex - catalogue.csv', 'quarterly_annex_data', FX_FR=True)
#data=EuropeanSemester()
#enlargement_yearly()
#esde=anyCatalogue('ESDE annex - catalogue.csv', 'esde_annex', FX_FR=True)
#esdeFab=anyCatalogue('ESDE Fabio charts - catalogue.csv','ESDE Fabio ch1', lite=True)

#g20=anyCatalogue('EU G20 self report - catalogue.csv','G20 self report', lite=True, join_labels=True)

#countryfiches=anyCatalogue('catalogue - country_fiches_geounits.csv','country_fiches_geounits', lite=True)
#countryfiches['period_type']=countryfiches['year'].str[4:5]
#countryfiches['y']=countryfiches['year'].str[0:4]
#countryfiches['q_m']=countryfiches['year'].str[4:]
#save_sync(countryfiches,'country_fiches_geounits')     
