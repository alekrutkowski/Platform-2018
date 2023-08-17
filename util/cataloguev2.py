# -*- coding: utf-8 -*-
"""
Created on Mon Jul  7 10:26:47 2014

@author: arranda
"""

#from formula_engine.engine import *
from formula_engine.engine_v2 import *
#from tools import * 
from util.catalogues import *

#Import specific indicators

#from Indicators.GHDI import *

 
eu28Countries=['EU28','EU27','EA19','BE','BG','CZ','DK','DE',	'EE',	'EL',	'IE',	'ES',	'FR', 'FX', 'HR',	'IT',	'CY',	'LV',	'LT',	'LU',	'HU',	'MT',	'NL',	'AT',	'PL',	'PT',	'RO',	'SI',	'SK',	'FI',	'SE',	'UK'	]

#As the FR series are shoreter we complete replace them by the FX series 
def replace_FX_FR(data):
    filesFX=set(data['file'][data.geo=='FX'])    
    print("Files with FR/FX problem")
    print(filesFX)
    final=data.copy()
    
    for indicator in set(data['IndicatorID'][data.geo=='FX']):
        #print(indicator)        
        #final=final[final.IndicatorID==indicator]  
        
        #Not for demographic files
        if 'demo' not in list(set(final[final.IndicatorID==indicator]['file']))[0]:
            #print(list(set(final[final.IndicatorID==indicator]['file']))[0])
            final=final[~((final.IndicatorID==indicator) & (final.geo=='FR'))]
            #This works if no FR records for year before 2014
            final.ix[(final.IndicatorID==indicator) & (final.geo=='FX'),'geo']='FR'
        
    return final
   



def speech():
    catalogue_standard='speech- catalogue.csv'
    outputFile='speech'   
    #Run specific calculated indicators for the project
   
    #Run catalogue
    cat_quaterly=catalogue(catalogue_standard)
    mergedFile=cat_quaterly.getAllData()
    #Run specific actions in the data file
    # 1) Filter years smaller than 2000    
    mergedFile=filterByYear(mergedFile, 1999)
    mergedFile['period_type']=mergedFile['year'].str[4:5]
    mergedFile['y']=mergedFile['year'].str[0:4]
    mergedFile['q_m']=mergedFile['year'].str[4:]
    
    save_sync(mergedFile,outputFile )
    return mergedFile


def JAF_health():
    catalogue_non_standard='JAF-HEALTH - catalogue_non_standard.csv'
    catalogue_standard='JAF-HEALTH - catalogue.csv'
    outputFile='jaf-health'   
    #Run specific calculated indicators for the project
    readExcelCatalogue("\\\\net1\\empl\\public\\JAF development\\JAF modules\\Health PA\\reference version\\JAF health - reference version.xlsm", "JAF-HEALTH")
    
    #Run formula engine for the project
    catalogueFormulas(catalogue_non_standard)
    
    #Run catalogue
    cat_radar=catalogue(catalogue_standard)
    mergedFile=cat_radar.getAllData()
    
    #Run specific actions in the data file
    mergedFile['geo']=mergedFile['geo'].replace('GR','EL')   
    #Add Reference year column in the data file for compatibility with old version
    refYearDict=cat_radar.getSpecialField('ReferenceYear')    
    mergedFile['ReferenceYear']=mergedFile.apply(lambda row: refYearDict[row['IndicatorID']], axis=1)    
    save_sync(mergedFile,outputFile)    
    
    #Post-calculations after file is saved
    
    specialCalculations(outputFile,10)
    
    return mergedFile


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
    mergedFile=mergedFile[mergedFile.geo.isin(eu28Countries)]
    #Add Reference year column in the data file for compatibility with old version    
    mergedFile=filterByYear(mergedFile, 1998)
    mergedFile=replace_FX_FR(mergedFile)
    save_sync(mergedFile,outputFile,3) 
    return mergedFile    
    


def guidanceNotes():
    catalogue_non_standard='guidance notes.csv'
    catalogue_standard='guidance notes.csv'
    outputFile='guidance notes'   
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
    mergedFile=mergedFile[mergedFile.geo.isin(eu28Countries)]
    #Add Reference year column in the data file for compatibility with old version    
    mergedFile=filterByYear(mergedFile, 1998)
    #mergedFile=replace_FX_FR(mergedFile)
    save_sync(mergedFile,outputFile,3) 
    return mergedFile 


def SPPM():
    #Extra files
    download_and_stack(['spr_exp_gdp','ilc_pees01'])
    #Dashboard
    #SPPM_dashboard=anyCatalogue('catalogue - SPMM_dashboard.csv','catalogue_non_standard - SPMM_dashboard.csv','SPMM_dashboard')
    
    #ANNEX   
    SPPM_annex=anyCatalogue('catalogue - SPMM_annex.csv','catalogue_non_standard - SPMM_annex.csv','SPMM_annex')
    
    #dashboard calculations
    
    #Venn diagrams
    return SPPM_annex

def basicCatalogue():
    catalogue_non_standard='catalogue_non_standard.csv'
    catalogue_standard='catalogue.csv'
    outputFile='global'    
    
    #Run specific calculated indicators for the project
    #ghdi_indicators()
    
    #Run formula engine for the project
    #formula_engine(catalogue_non_standard)
    catalogueFormulas(catalogue_non_standard)
    
    #Run catalogue
    cat_quaterly=catalogue(catalogue_standard)
    mergedFile=cat_quaterly.getAllData()
    #Run specific actions in the data file
   
    save_sync(mergedFile,outputFile )
    return mergedFile


#lite True means that only basic colimns will be produced: geo, year, value_n, values, flag, file
def anyCatalogue(cat_standard, cat_non_standard, file_output, lite=False, FX_FR=False):    
    if cat_non_standard!='':
        catalogueFormulas(cat_non_standard) # calls a special function for formulas in engine_v2   
    myCatalogue=catalogue(cat_standard) # instantiate a catalogue object
    mergedFile=myCatalogue.getAllData() # Gets data by using the function getAllData
    
    if lite:
        mergedFile=pd.DataFrame(mergedFile,columns=['IndicatorID','geo','year','values','value_n','flag','file'])
    
    #FR/FX issue
    if FX_FR:
        mergedFile=replace_FX_FR(mergedFile)
    #Run specific actions in the data file   
    #save_sync(mergedFile,file_output)
    return mergedFile


def save_sync(mergedFile,outputFile, decimal_numbers=2):
    #Save file
    #Force conversion to numeric to avoid problems with last decimal number in non-standard
    mergedFile['value_n']=pd.to_numeric(mergedFile['value_n'])    
    mergedFile.to_csv(merged_path+outputFile+'.csv',index=False, float_format='%.'+str(decimal_numbers)+'f')
    #Sync folders
    syncFolders(merged_path,merged_path_p)    



#Inequalities=anyCatalogue('catalogue - JER Scoreboard.csv', 'catalogue - JER Scoreboard.csv', 'test', lite=True, FX_FR=False)





