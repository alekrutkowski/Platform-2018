import os

# Define the file path
file_path = r'H:\Data\Participation in education and training (excluding guided on the job training).xlsx'
# Check if the file exists
if not os.path.exists(file_path):
    raise FileNotFoundError("The file is not present in the specified directory:\n" + file_path +
                            "\nYou can download it from:\n" +
                            "https://circabc.europa.eu/ui/group/d14c857a-601d-438a-b878-4b4cebd0e10f/library/c5a8b987-1e37-44d7-a20e-2c50d6101d27/details" +
                            "\nor get from Elodie CAYOTTE (ESTAT) <Elodie.CAYOTTE@ec.europa.eu> or Sabine GAGEL (ESTAT) <Sabine.GAGEL@ec.europa.eu>"
                            )

import pandas as pd


# List of tuples with (sheet_name_prefix, usecols, new_column_names)
sheets_and_columns = [
    ('SEX', 'A,E,F,G', ['geo','TOTAL','MEN','WOMEN']),
    ('AGE', 'A,H,I,J,K', ['geo','Y25-34','Y35-44','Y45-54','Y55-64']),
    ('ISCED', 'A,G,H,I', ['geo','ISCED_0-2','ISCED_3-4','ISCED_5-8'])
]

# List to store each imported DataFrame
dataframes = []
for sheet_name_prefix, usecols, colnames in sheets_and_columns:
    for year in [2016, 2022]:
        # Import rows 5 to 33
        # Note: Python uses 0-based indexing, Excel uses 1-based indexing
        # skiprows=4 skips the first 4 rows, and nrows=28 reads the next 29 rows (column header + 28 data rows)
        df = pd.read_excel(file_path,
                           sheet_name=sheet_name_prefix+' - '+str(year),
                           skiprows=5,
                           nrows=28,
                           usecols=usecols,
                           header=None)
        df.columns = colnames
        df['year'] = year
        df = pd.melt(df, id_vars=['geo','year'], var_name='group', value_name='value_n')
        # Append the DataFrame to the list
        dataframes.append(df)

# Concatenate all DataFrames verticlly
df = pd.concat(dataframes, axis=0).reset_index(drop=True)

Eurostat_country_codes = {
    "EU-27": "EU27_2020",
    "Belgium": "BE",
    "Bulgaria": "BG",
    "Czechia": "CZ",
    "Denmark": "DK",
    "Germany": "DE",
    "Estonia": "EE",
    "Ireland": "IE",
    "Greece": "EL",  # Note: Eurostat uses EL for Greece, not GR
    "Spain": "ES",
    "France": "FR",
    "Croatia": "HR",
    "Italy": "IT",
    "Cyprus": "CY",
    "Latvia": "LV",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Hungary": "HU",
    "Malta": "MT",
    "Netherlands": "NL",
    "Austria": "AT",
    "Poland": "PL",
    "Portugal": "PT",
    "Romania": "RO",
    "Slovenia": "SI",
    "Slovakia": "SK",
    "Finland": "FI",
    "Sweden": "SE",
}
# Replace the country names in the "geo" column with their Eurostat codes
df['geo'] = df['geo'].apply(lambda x: Eurostat_country_codes.get(x, x))
df['flag'] = ""
# Convert 'value_n' column to floats
df['value_n'] = pd.to_numeric(df['value_n'], errors='coerce')
df['file'] = 'Participation_in_education_and_training'
Participation_in_education_and_training = \
    df[['year', 'geo', 'file', 'group', 'value_n', 'flag']]

## Artificially make the second-latest-available year = latest-available-year minus 3 to fit the subsequent scoreboard methodology => to be then correctrd in the Excel output
latest_year = Participation_in_education_and_training['year'].max()
second_latest_year = sorted(Participation_in_education_and_training['year'].unique())[-2]
# Update the DataFrame: change the second-latest year to target year
Participation_in_education_and_training['year'] = \
    Participation_in_education_and_training['year'].replace(second_latest_year, latest_year - 1)
# Write the DataFrame to a CSV file
Participation_in_education_and_training.to_csv(
    r'H:\Data\non_standard\calculated\Participation_in_education_and_training.csv', index=False)

# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 17:14:37 2017

@author: badeape
"""

# comment out all commands in call_catalogue (why though?)
from call_catalogue import anyCatalogue
from formula_engine.engine_v2 import *
from util.tools import *
from util.catalogues import *
from config.config_scoreboard import *

import matplotlib.pyplot as plt
import xlsxwriter


# ******************  Functions definitions  *****************************************

# Get value from catalogue
def getField(Indicator, Field):
    return  catalogueJER.loc[Indicator][Field]

#Set value in catalogue
def setField(Indicator, Field, Value):
    catalogueJER.loc[Indicator, Field]=Value

# Scores
def calculate_score(df, column_name, ref_Point, y, ID):
    wk_data=df.copy()
    wk_data=wk_data[wk_data.geo.isin(CtryList)]
    #indicator = set(wk_data['Indicator']).pop()
    score_mean=0
    score_std=0
    sense=getField(ID, 'sense')
    # Non-weighted EU28 average
    #TODO: replace nulls in the catalogue by the real value 'avg'
    if ref_Point=='avg' or ref_Point=='':
        score_mean=wk_data[column_name].mean()
    elif ref_Point=='EU27_2020':
        score_mean=df[df.geo=='EU27_2020'].iloc[0][column_name]
    elif np.isreal(ref_Point):
        score_mean=ref_Point
    else:
        Exception("No valid Reference point defined for indicator" + ID)

    score_std=(((df[column_name]-score_mean)**2).sum()/(df[column_name].count()))**0.5
    #print(ID, column_name, ref_Point, round(score_mean,2), round(score_std,2) )
    df['score_'+column_name]= (df[column_name]- score_mean) / score_std
    if sense =='neg':
        df['score_'+column_name]= -1*df['score_'+column_name]
#    cutoff.loc[len(cutoff)] = [ID, column_name, ref_Point, round(float(score_mean)), round(float(score_std)),round(float(score_mean-score_std)),round(float(score_mean-score_std/2)),round(float(score_mean+score_std/2)),round(float(score_mean+score_std))]
    cutoff.loc[len(cutoff)] = [ID, y, score_mean, score_std, score_mean-score_std ,score_mean-score_std/2, score_mean+score_std/2, score_mean+score_std]

    return df
# cutoff = pd.DataFrame(columns=('Indicator', 'type', 'refPoint', 'mean', 'std','t1','t2','t3','t4'))

# Set categories
def getCategories(x):
    myLevel = x['score_value_n']
    myChange = x['score_ychange']
    if myLevel < -1 and myChange < 1:
        return 1 #'r'
    elif (-1 <= myLevel < -0.5) or (myLevel < -1 and 1 <= myChange) or ( -0.5 <= myLevel < 0.5 and  myChange < -1):
        return 2 #'orange'
    elif  -0.5 <= myLevel < 0.5 and -1 <= myChange < 1 :
        return 3 #'lightgray'
    elif (0.5 <= myLevel < 1) or (myLevel >= 1 and myChange <-1) or ( -0.5 <= myLevel < 0.5 and  myChange >= 1):
        return 4 #'lime'
    elif myLevel >= 1 and myChange >= -1:
        return 5 #'g'
    else:
        return 'c'

# Labels for levels
def getLabelsLevel(x):
    myLevel = x['score_value_n']
    if myLevel < -1: return 'Very low'
    elif (-1 <= myLevel < -0.5): return 'Low'
    elif ( -0.5 <= myLevel < 0.5): return 'On average'
    elif (0.5 <= myLevel < 1): return 'High'
    elif myLevel >= 1: return 'Very high'
    else: return 'c'

# Labels for changes
def getLabelsChanges(x):
    myLevel = x['score_ychange']
    if myLevel < -1: return 'Much lower than average'
    elif (-1 <= myLevel < -0.5): return 'Lower than average'
    elif ( -0.5 <= myLevel < 0.5): return 'On average'
    elif (0.5 <= myLevel < 1): return 'Higher than average'
    elif myLevel >= 1: return 'Much higher than average'
    else: return 'c'


def getScoreboardData(cat):
    print('Data download...')
    data=anyCatalogue(cat, extractionFile, lite=True)
    # This moment data has all indicators, for all countries and for all years
    print('Data downloaded.')
    # Merge with the catalogue to extract different categories of indicators which are mentioned in the catalogue only
    data.columns=['IND_CODE','geo','year','values','value_n','flag','file']
    data = pd.merge(data,catalogueJER,on=['IND_CODE'])
    data = data[['IND_CODE','Indicator','type','Order','lastYear','sense','change','Group','geo','year','value_n','flag']]
    return data

def setLastYear(dataset):
    for indic in codes:
        print('Setting the last year for indicator: ',indic)

        if(indic == 'ID13'):
            year=2018
        elif(indic == 'ID21'):
            year=2018
        elif(indic == 'ID58'):
            year=2020
        elif(indic == 'ID59'):
            year=2020
        elif(indic == 'ID60'):
            year=2020
        elif(indic == 'ID61'):
            year=2023
        elif(indic == 'ID118'):
            year=2022
        elif(indic == 'ID4'):
            year=2023
        else:
            year = dataset[(dataset.IND_CODE==indic) & (dataset.geo=='EU27_2020') & (~dataset.value_n.isnull())].year.max()
        setField(indic,'lastYear',year)
    return dataset

# ******************  END definitions  **************************************************

# ********************   MAIN PROGRAM    ************************************************

#************************************************************************************************
# ***** -------- Step 1: load catalogue, extract and save levels ------ *****
#************************************************************************************************
# Load catalogue
for i in range(1):
    print('')
catalogueJER=pd.read_csv(root_path_n+JER_catalogue)  # open the catalogue into a data frame - from G drive
catalogueJER = catalogueJER.fillna('')              # deletes NaNs and fill the gaps
codes=set(catalogueJER['IND_CODE'])

# extract data
JER_Scoreboard = getScoreboardData(JER_catalogue)
JER_Scoreboard_II = JER_Scoreboard.copy()

#inserting "last year" in the catalogue
catalogueJER.set_index('IND_CODE',inplace=True)
JER_Scoreboard = setLastYear(JER_Scoreboard)
catalogueJER.reset_index(inplace=True)

# Save all data
for i in range(1):
    print('')
print('Saving all extracted data...')
JER_Scoreboard.to_csv(localpath+extractionFile) # Data on levels saved: all indicators, all years, all countries, EU included
catalogueJER.to_csv(localpath+'updatedCatalogue.csv')

# *****************************************************************************************************
# ***** ---- Step 2 extract the headline indicators, calculate and save scores and changes for them ---- *****
# ******************************************************************************************************
# Extract the headline indicators for score calculation
# Calculate Scores
JER_Scoreboard_h = JER_Scoreboard[JER_Scoreboard.type=='H']  # Filter for headline indicators for which scores are required
catalogueJER=catalogueJER.set_index(['IND_CODE'])          # sets the index
# JER_Scoreboard has headline indicators only, for all countries and for all years

# Cut offs data set - create as an empty data set
cutoff = pd.DataFrame(columns=('Indicator', 'year', 'mean', 'std','t1','t2','t3','t4'))

# For all headline indicators and all years and for MS only, it calculates scores

for i in range(1):
    print('')
print('Calculating scores for headline indicators...')
scores = pd.DataFrame()
for indic in set(JER_Scoreboard_h['IND_CODE']):
    print('Calculating scores for headline indicator...'+indic+'...')
    for year in set(JER_Scoreboard_h['year']):
        tmp = JER_Scoreboard_h[(JER_Scoreboard_h.IND_CODE==indic) & (JER_Scoreboard_h.year==year) &(JER_Scoreboard_h.geo.isin(CtryList))]
        # scores=scores.append(calculate_score(tmp, 'value_n', 'avg', year, indic))
        scores = pd.concat([scores, calculate_score(tmp, 'value_n', 'avg', year, indic)], ignore_index=True) # https://stackoverflow.com/a/75956237

# Calculate annual changes
for i in range(1):
    print('')
print('Calculating annual changes for headline indicators...')
changes = pd.DataFrame()
for indic in set(JER_Scoreboard_h['IND_CODE']):
    print('Calculating  annual changes for the indicator '+indic+'...')
    for country in CtryList:
        ch=''
        tmp = JER_Scoreboard_h[(JER_Scoreboard_h.IND_CODE==indic) & (JER_Scoreboard_h.geo==country)]
        tmp['flag']=tmp['flag'].replace(np.nan,'')
        tmp=tmp.sort_values('year')
        if len(tmp)>0: ch = tmp.iloc[0]['change']
        if ch=='pp':  tmp['ychange'] = tmp['value_n'].diff()
        elif ch=='%': tmp['ychange'] = tmp['value_n'].pct_change(fill_method=None) # fill_method=None to avoid incorrect ychange=0 when value_n=missing (should be ychange=missing i.e. np.nan)
        tmp['ychange_flag']=tmp['flag']+tmp['flag'].shift(1).replace('b','')
        if len(tmp)>0: tmp['ychange_flag']=tmp['ychange_flag'].replace(np.nan,'')
        if len(tmp)>0: tmp['ychange_flag'] = tmp.apply(lambda x: "".join(set(x['ychange_flag'])), axis=1)
        if (tmp['IND_CODE'] == 'ID4').any(): # if not empty
            tmp.loc[(tmp['IND_CODE']=='ID4') & tmp['value_n'].notna() & tmp['ychange'].isna(),
                    'ychange'] = 0 # EXCEPTIONAL - TEMPORARY !!! ★
        # changes=changes.append(tmp)
        changes = pd.concat([changes, tmp], ignore_index=True)  # https://stackoverflow.com/a/75956237

#OLD (net earnings not used anymore)
# Overwrite the changes for mixed indicators from the external file: net earnings! HARD CODED the rank of the indicator
#changes = changes[(changes.IND_CODE != 'ID74')] #delete first that indicator - HARD CODED
#net_earnings = pd.read_csv(calculated_path+'net_earnings.csv')
#changes = changes.append(net_earnings)

changes.to_csv(localpath+'changes.csv',index=False, float_format='%.4f')

# Calculate scores for annual changes
for i in range(2):
    print('')
print('Calculating scores for annual changes - headline indicators...')
scoresD = pd.DataFrame()
for indic in set(changes['IND_CODE']):
    print('Calculating  scores for the indicator '+indic+'...')
    for year in set(changes['year']):
        tmp = changes[(changes.IND_CODE==indic) & (changes.year==year)]
        # scoresD = scoresD.append(calculate_score(tmp, 'ychange', 'avg', year, indic))
        scoresD = pd.concat([scoresD, calculate_score(tmp, 'ychange', 'avg', year, indic)], ignore_index=True)  # https://stackoverflow.com/a/75956237

#scoresD = scoresD[(scoresD.geo.isin(CtryList))]
scoresD = scoresD[['IND_CODE','Indicator','geo','year','ychange','ychange_flag','score_ychange']]

# Merge scores for levels with scores for differences
scores = pd.merge(scores,scoresD,on=['IND_CODE','Indicator','geo','year'])

scores.loc[(scores['IND_CODE']=='ID4') & (scores['year']==2021) & (scores['score_ychange'].isna()),
           'score_ychange'] = 0  # EXCEPTIONAL - TEMPORARY !!! ★

#Calculate color categories and apply labels
#scores=scores[(scores.year>=2015)]
print('Labeling data - headline indicators...')
scores['score_value_n']=scores['score_value_n']*(-1)
scores['score_ychange']=scores['score_ychange']*(-1)
scores['category']=scores.apply(getCategories, axis=1)
scores['LabelL']=scores.apply(getLabelsLevel, axis=1)
scores['LabelD']=scores.apply(getLabelsChanges, axis=1)

print('Calculating the last available year...')
JER_Scores = pd.DataFrame()
for indic in set(scores['IND_CODE']):
    tmp = scores[(scores.IND_CODE==indic) & (scores.year==getField(indic,'lastYear'))]
    # JER_Scores = JER_Scores.append(tmp)
    JER_Scores = pd.concat([JER_Scores, tmp], ignore_index=True)  # https://stackoverflow.com/a/75956237

# For the SCF file - ID122 to be included here
scores.columns=['code','indicator','type','Order','lastYear','sense','change','group','geo','year','level','flag','scoreL','ydiff','ydiff_flag','scoreD','category','LabelL','LabelD']
scores.to_csv(localpath+'SCORES_all_years.csv')   # Scores saved: headline indicators, all countries, all years

scores= JER_Scores
# Prepare the dataframe for saving
scores.columns=['code','indicator','type','Order','lastYear','sense','change','group','geo','year','level','flag','scoreL','ydiff','ydiff_flag','scoreD','category','LabelL','LabelD']
# scores = scores[scores['code']!='ID122'] # EXCEPTIONAL - TEMPORARY !!! ★
# scores.loc[(scores['code']=='ID4') & (scores['year']==2021) & (scores['scoreD'].isna()),
#            'scoreD'] = 0  # EXCEPTIONAL - TEMPORARY !!! ★
# scores.loc[(scores['code']=='ID4') & (scores['year']==2021) & (scores['LabelD'].isna()),
#            'LabelD'] = 'On average'  # EXCEPTIONAL - TEMPORARY !!! ★
# Save the scores
scores.to_csv(localpath+'SCORES.csv')   # Scores saved: headline indicators, all countries, last year only

# Fiches with headline indicators - scores by country
for i in range(2):
    print('')
print('Producing fiches with headline indicators - scores by country...')
writer = pd.ExcelWriter(localpath+'fiches.xlsx')
for ctry in set(scores['geo']):
    tmp = scores[scores.geo==ctry]
    pivot = pd.pivot_table(tmp,values = ["scoreL","scoreD"],index=['indicator'],columns=['geo'])
    pivot.to_excel(writer,ctry)
# writer.save()
writer.close() # https://stackoverflow.com/a/76119258

# ************************************************************************************************************
# ***** ---- Step 3 - Producing data on levels and yearly changes for the last three years for all indicators...
# ************************************************************************************************************

JER_Scoreboard_b=pd.read_csv(localpath+extractionFile)
JER_Scoreboard_b = JER_Scoreboard_b[['IND_CODE','Indicator','type','Order','change','geo','year','value_n','flag']]
# JER_Scoreboard_b = JER_Scoreboard_b[JER_Scoreboard_b['IND_CODE']!='ID122'] # EXCEPTIONAL - TEMPORARY !!! ★

# Calculate annual changes
for i in range(1):
    print('')
print('Producing data for the last three years for all indicators...')
for i in range(1):
    print('')
changes = pd.DataFrame()
i=0
for indic in set(JER_Scoreboard_b['IND_CODE']):
    i+=1
    print('Producing data for the last three years for indicator '+str(i)+' out of 121 - '+indic+'...')
    for country in ExCtryList:
        ch=''
        tmp = JER_Scoreboard_b[(JER_Scoreboard_b.IND_CODE==indic) & (JER_Scoreboard_b.geo==country)]
        tmp['flag']=tmp['flag'].replace(np.nan,'')
        tmp=tmp.sort_values('year')
        if len(tmp)>0: ch = tmp.iloc[0]['change']
        if ch=='pp':  tmp['ychange'] = tmp['value_n'].diff()
        elif ch=='%': tmp['ychange'] = 100*tmp['value_n'].pct_change(fill_method=None) # fill_method=None to avoid incorrect ychange=0 when value_n=missing (should be ychange=missing i.e. np.nan)
        tmp['ychange_flag']=tmp['flag']+tmp['flag'].shift(1).replace('b','')
        if len(tmp)>0: tmp['ychange_flag']=tmp['ychange_flag'].replace(np.nan,'')
        if len(tmp)>0: tmp['ychange_flag'] = tmp.apply(lambda x: "".join(set(x['ychange_flag'])), axis=1)
        if (tmp['IND_CODE'] == 'ID4').any(): # if not empty
            tmp.loc[(tmp['IND_CODE']=='ID4') & tmp['value_n'].notna() & tmp['ychange'].isna(),
                    'ychange'] = 0 # EXCEPTIONAL - TEMPORARY !!! ★
        # changes=changes.append(tmp)
        changes = pd.concat([changes, tmp], ignore_index=True)  # https://stackoverflow.com/a/75956237

changes = changes[['IND_CODE','geo','year','ychange','ychange_flag']]

# This file will contains levels and changes for all indicators, all years but only EU countries. Plus, the yearly changes for all
JER_Scoreboard_b = pd.merge(JER_Scoreboard_b,changes,on=['IND_CODE','geo','year'])

# Save levels and changes
JER_Scoreboard_b.to_csv(localpath+'JER_scoreboard_data_b.csv') # Data on levels and changes saved: all indicators, all EU countries

JER_Scoreboard = pd.DataFrame()
for indic in set(JER_Scoreboard_b['IND_CODE']):
    year=getField(indic,'lastYear')
    tmp = JER_Scoreboard_b[(JER_Scoreboard_b.IND_CODE==indic) & ((JER_Scoreboard_b.year==year) | (JER_Scoreboard_b.year==year-1) |(JER_Scoreboard_b.year==year-2))]
    # JER_Scoreboard = JER_Scoreboard.append(tmp)
    JER_Scoreboard = pd.concat([JER_Scoreboard, tmp], ignore_index=True)  # https://stackoverflow.com/a/75956237

JER_Scoreboard.to_csv(localpath+'JER_scoreboard.csv') # Data on levels and changes saved: all indicators, last three years, all EU countries
ranking = pd.read_csv(localpath+'Countries_ranking.csv')

# ************************************************************************************************************
# ***** ---- Step 4 - Calculating differences and distances for all indicators
# ************************************************************************************************************

print('Calculating differences for all indicators...')
JER_Scoreboard_b=pd.read_csv(localpath+'JER_scoreboard.csv')
# JER_Scoreboard_b = JER_Scoreboard_b[JER_Scoreboard_b['IND_CODE']!='ID122'] # EXCEPTIONAL - TEMPORARY !!! ★
JER_Scoreboard = pd.DataFrame()
for indic in set(JER_Scoreboard_b['IND_CODE']):
    year=getField(indic,'lastYear')
    tmp = JER_Scoreboard_b[(JER_Scoreboard_b.IND_CODE==indic) & ((JER_Scoreboard_b.year==year) | (JER_Scoreboard_b.year==year-1) |(JER_Scoreboard_b.year==year-2))]
    # JER_Scoreboard = JER_Scoreboard.append(tmp)
    JER_Scoreboard = pd.concat([JER_Scoreboard, tmp], ignore_index=True)  # https://stackoverflow.com/a/75956237
for i in range(2):
    print('')
JER_Scoreboard_diff = pd.DataFrame()
for indic in set(JER_Scoreboard['IND_CODE']):
    print('Calculating differences for indicator...'+indic+'...')
    for year in set(JER_Scoreboard['year']):

#See the caveats in the documentation: https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
#   aggEU['geo']='EUnw'
# /Users/fabioraffa/Documents/Fabio Work/Platform 2018/tools/scoreboard/scoreboard_y.py:334: SettingWithCopyWarning:
# A value is trying to be set on a copy of a slice from a DataFrame.
# Try using .loc[row_indexer,col_indexer] = value instead

        aggEA = pd.DataFrame()
        aggEU = pd.DataFrame()
        tmpEU = JER_Scoreboard[(JER_Scoreboard.IND_CODE==indic) & (JER_Scoreboard.year==year) & (JER_Scoreboard.geo.isin(CtryList))]
        tmpEA = JER_Scoreboard[(JER_Scoreboard.IND_CODE==indic) & (JER_Scoreboard.year==year) & (JER_Scoreboard.geo.isin(EAList))]
        aggEA = tmpEU[tmpEU.geo=='AT']
        aggEU = tmpEU[tmpEU.geo=='AT']
        aggEU['geo']='EUnw'
        aggEA['geo']='EAnw'
        aggEU['value_n']=tmpEU['value_n'].mean()
        aggEA['value_n']=tmpEA['value_n'].mean()
        aggEU['ychange']=tmpEU['ychange'].mean()
        aggEA['ychange']=tmpEA['ychange'].mean()
        tmpEU = JER_Scoreboard[(JER_Scoreboard.IND_CODE==indic) & (JER_Scoreboard.year==year) & (JER_Scoreboard.geo.isin(ExCtryList))]
        # tmpEU = tmpEU.append(aggEU)
        tmpEU = pd.concat([tmpEU, aggEU], ignore_index=True)  # https://stackoverflow.com/a/75956237
        # tmpEU = tmpEU.append(aggEA)
        tmpEU = pd.concat([tmpEU, aggEA], ignore_index=True)  # https://stackoverflow.com/a/75956237
        tmpEU['EUnwL'] = aggEU['value_n'].mean()
        tmpEU['EUnwD'] = aggEU['ychange'].mean()
        tmpEU['DistEU'] = tmpEU['value_n'] - tmpEU['EUnwL']
        tmpEU['DiffMSEU'] = tmpEU['ychange'] - tmpEU['EUnwD']
        # JER_Scoreboard_diff = JER_Scoreboard_diff.append(tmpEU)
        JER_Scoreboard_diff = pd.concat([JER_Scoreboard_diff, tmpEU], ignore_index=True)  # https://stackoverflow.com/a/75956237

JER_Scoreboard_diff['flag']=JER_Scoreboard_diff['flag'].replace(np.nan,'')
JER_Scoreboard_diff['ychange_flag']=JER_Scoreboard_diff['ychange_flag'].replace(np.nan,'')
JER_Scoreboard_diff.to_csv(localpath+'JER_scoreboard_diff_check.csv')
JER_Scoreboard_diff = JER_Scoreboard_diff[['IND_CODE','Indicator','type','Order','change','geo','year','value_n','flag','ychange','ychange_flag','DistEU','DiffMSEU']]
headline = JER_Scoreboard_diff[JER_Scoreboard_diff.type=='H']
headline.to_csv(localpath+'JER_scoreboard_diff_head.csv',index=False, float_format='%.3f')  # Save here only the headline indicators
JER_Scoreboard_diff.to_csv(localpath+'JER_scoreboard_diff.csv',index=False, float_format='%.3f')  # Save all indicators. In contains data in headline

# ************************************************************************************************************
# ***** ---- Step 5 - Preparing data for output
# ************************************************************************************************************

print('Preparing data for output...')
table = pd.read_csv(localpath+'JER_scoreboard.csv')
# table = table[table['IND_CODE']!='ID122'] # EXCEPTIONAL - TEMPORARY !!! ★
table = table[['IND_CODE','Indicator','type','Order','change','geo','year','value_n','flag','ychange','ychange_flag']]

JER_Scoreboard_agg=pd.read_csv(localpath+'JER_scoreboard_diff.csv')
JER_Scoreboard_agg = JER_Scoreboard_agg[['IND_CODE','Indicator','type','Order','change','geo','year','value_n','flag','ychange','ychange_flag']]
aggNW = JER_Scoreboard_agg[JER_Scoreboard_agg.geo.isin(AggNWList)]
# table=table.append(aggNW)
table = pd.concat([table, aggNW], ignore_index=True)  # https://stackoverflow.com/a/75956237
table = pd.merge(ranking,table,on=['geo'])
table['flag']=table['flag'].replace(np.nan,'')
table['ychange_flag']=table['ychange_flag'].replace(np.nan,'')
table['levelflag'] = table['value_n'].astype(str)+" "+table['flag']

headline = table[table.type=='H']
headline=headline.sort_values('Order')
pivoth=pd.pivot_table(headline,values='value_n',index=['rank','geo'],columns=['Order','Indicator','year'])
pivotf=pd.pivot_table(headline,values='flag',index=['rank','geo'],columns=['Order','Indicator','year'],aggfunc=lambda x: ' '.join(x))
pivothf=pd.pivot_table(headline,values='levelflag',index=['rank','geo'],columns=['Order','Indicator','year'],aggfunc=lambda x: ' '.join(x))
supl = table[table.type=='S']
supl=supl.sort_values('Order')
pivots=pd.pivot_table(supl,values='value_n',index=['rank','geo'],columns=['Order','Indicator','year'])
pivotsf=pd.pivot_table(supl,values='levelflag',index=['rank','geo'],columns=['Order','Indicator','year'],aggfunc=lambda x: ' '.join(x))
components = table[table.type=='C']
components=components.sort_values('Order')
pivotcomp=pd.pivot_table(components,values='value_n',index=['rank','geo'],columns=['Order','Indicator','year'])
pivotcompf=pd.pivot_table(components,values='levelflag',index=['rank','geo'],columns=['Order','Indicator','year'],aggfunc=lambda x: ' '.join(x))
compb = table[table.type=='CB']
compb=compb.sort_values('Order')
pivotcb=pd.pivot_table(compb,values='value_n',index=['rank','geo'],columns=['Order','Indicator','year'])
pivotcbf=pd.pivot_table(compb,values='levelflag',index=['rank','geo'],columns=['Order','Indicator','year'],aggfunc=lambda x: ' '.join(x))
breakdowns = table[table.type=='B']
breakdowns=breakdowns.sort_values('Order')
pivotb=pd.pivot_table(breakdowns,values='value_n',index=['rank','geo'],columns=['Order','Indicator','year'])
pivotbf=pd.pivot_table(breakdowns,values='levelflag',index=['rank','geo'],columns=['Order','Indicator','year'],aggfunc=lambda x: ' '.join(x))
supbreak = table[table.type=='SB']
supbreak=supbreak.sort_values('Order')
pivotsb=pd.pivot_table(supbreak,values='value_n',index=['rank','geo'],columns=['Order','Indicator','year'])
pivotsbf=pd.pivot_table(supbreak,values='levelflag',index=['rank','geo'],columns=['Order','Indicator','year'],aggfunc=lambda x: ' '.join(x))

print('Saving data for comparison 2008 - 2013 - last available...')
compare = pd.read_csv(localpath+extractionFile)
compare = pd.merge(ranking,compare,on=['geo'])
compare = compare[(compare.type=='H') & (compare.geo.isin(ExCtryList))]

comp = pd.DataFrame() # years HARD CODED
for indic in set(compare.IND_CODE) :
    year=getField(indic,'lastYear')
    tmp=compare[(compare.IND_CODE==indic) &((compare.year==2008) | (compare.year==2013) | (compare.year==pd.to_numeric(year)))]
    # comp=comp.append(tmp)
    comp = pd.concat([comp, tmp], ignore_index=True)  # https://stackoverflow.com/a/75956237
compare=comp.sort_values('Order')
pivotc=pd.pivot_table(compare,values='value_n',index=['rank','geo'],columns=['Order','Indicator','year'])

scores = pd.merge(ranking,scores,on=['geo'])
scores = scores[['geo','rank','code','indicator','Order','scoreL','scoreD']]
scores.columns = ['geo','rank','code','indicator','Order','score1_L','score2_D']
scores = scores.set_index(['geo','rank','code','indicator','Order'])
scores = scores.stack()
scores = scores.reset_index()
scores.columns =['geo','rank','code','indicator','Order','score_type','value']
pivot_scores = pd.pivot_table(scores,values='value',index=['rank','geo'],columns=['Order','indicator','score_type'])

JER_Scoreboard_diff = pd.read_csv(localpath+'JER_scoreboard_diff.csv')
JER_Scoreboard_diff = JER_Scoreboard_diff[JER_Scoreboard_diff.type=='H']
JER_Scoreboard_diff = pd.merge(ranking,JER_Scoreboard_diff,on=['geo'])
JER_Scoreboard_diff = JER_Scoreboard_diff[['IND_CODE','Indicator','Order','geo','rank','year','ychange','DistEU','DiffMSEU']]
JER_Scoreboard_diff.columns=['IND_CODE','Indicator','Order','geo','rank','year','Change','Diff_EU','Diff_MSEU']
JER_Scoreboard_diff = JER_Scoreboard_diff.set_index(['IND_CODE','Indicator','Order','geo','rank','year'])
JER_Scoreboard_diff = JER_Scoreboard_diff.stack()
JER_Scoreboard_diff = JER_Scoreboard_diff.reset_index()
JER_Scoreboard_diff.columns=['IND_CODE','Indicator','Order','geo','rank','year','diff','value']
JER_Scoreboard_diff.to_csv(localpath+'JER_scoreboard_diff_pivot.csv',index=False, float_format='%.3f')
table = pd.read_csv(localpath+'JER_scoreboard_diff_pivot.csv')

diff = pd.DataFrame() # years HARD CODED
for indic in set(table.IND_CODE) :
    yr=getField(indic,'lastYear')
    tmp=table[(table.IND_CODE==indic) &((table.year==2008) | (table.year==2013) | (table.year==pd.to_numeric(yr)))]
    # diff=diff.append(tmp)
    diff = pd.concat([diff, tmp], ignore_index=True)  # https://stackoverflow.com/a/75956237
table=diff.sort_values('Order')

pivot_diff = pd.pivot_table(table,values='value',index=['rank','geo'],columns=['Order','Indicator','year','diff'])
pivot_diff=pivot_diff.reset_index()

# ************************************************************************************************************
# ***** ---- Step 6 - Output
# ************************************************************************************************************

print('Output files...')
writer = pd.ExcelWriter(localpath+'output.xlsx')
pivoth.to_excel(writer,'Headline')
pivotf.to_excel(writer,'Flags')
pivothf.to_excel(writer,'Headline_flags')
pivot_diff.to_excel(writer,'Differences')
pivot_scores.to_excel(writer,'Scores')
pivotcomp.to_excel(writer,'Components')
pivotcompf.to_excel(writer,'Components_flags')
pivotcb.to_excel(writer,'Components breakdowns')
pivotcbf.to_excel(writer,'Components breakdowns_flags')
pivotb.to_excel(writer,'Breakdowns')
pivotbf.to_excel(writer,'Breakdowns_flags')
pivots.to_excel(writer,'Supplementary')
pivotsf.to_excel(writer,'Supplementary_flags')
pivotsb.to_excel(writer,'Supplementary breakdowns')
pivotsbf.to_excel(writer,'Supplementary breakdowns_flags')
pivotc.to_excel(writer,'Comparison')
cutoff.to_excel(writer,'Cut_offs')

cutoff_copy = cutoff.copy()
cutoff_copy['cum_count'] = cutoff_copy.groupby(['Indicator', 'year']).cumcount() + 1
cutoff_copy['Level or change'] = cutoff_copy['cum_count'].map({1: 'Levels', 2: 'Changes'})
cutoff_copy.drop('cum_count', axis=1, inplace=True)
cutoff_copy = cutoff_copy[['Indicator', 'year', 'Level or change', 't1', 't2', 't3', 't4']]
non_missing_rows = cutoff_copy.dropna(subset=['t1', 't2', 't3', 't4'])
max_years = non_missing_rows.groupby(['Indicator','Level or change'])['year'].max().reset_index()
cutoff_copy = pd.merge(cutoff_copy, max_years, on=['Indicator','Level or change','year'], how='inner')
cutoff_copy.drop('year', axis=1, inplace=True)
cutoff_copy = cutoff_copy.rename(columns={'Indicator': 'IND_CODE'})
cutoff_copy.loc[(cutoff_copy['IND_CODE']=='ID61') & (cutoff_copy['Level or change']=='Changes'), # ID61 = GDHI per capita growth (2008=100)
                'Level or change'] = 'Changes (%)'
cutoff_copy.loc[(cutoff_copy['IND_CODE']=='ID61') & (cutoff_copy['Level or change']=='Changes (%)'), # ID61 = GDHI per capita growth (2008=100)
                ['t1', 't2', 't3', 't4']] *= 100
cutoff_copy = pd.merge(cutoff_copy, JER_Scoreboard_II[['IND_CODE','Indicator']].drop_duplicates(),
                       on=['IND_CODE'], how='inner')
cutoff_copy['IND_CODE_num'] = cutoff_copy['IND_CODE'].str.extract('(\d+)').astype(int)
cutoff_copy.sort_values(by=['IND_CODE_num', 'Indicator'], ascending=[True, True], inplace=True)
cutoff_copy.drop('IND_CODE_num', axis=1, inplace=True)
cutoff_copy = cutoff_copy[['Indicator','Level or change', 't1', 't2', 't3', 't4']]
cutoff_copy.to_excel(writer,'Cut_offs II', index=False)

# writer.save()
writer.close() # https://stackoverflow.com/a/76119258

# ********************   END OF MAIN PROGRAMME    ************************************************

print('Programme ready')