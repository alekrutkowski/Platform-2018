# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 15:42:13 2014

@author: arranda
"""
import pandas as pd
import numpy as np



#baseUrl='http://epp.eurostat.ec.europa.eu/NavTree_prod/everybody/BulkDownloadListing?sort=1&downfile=data%2F'
#After redesign
baseUrl='https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/'
#Number of days minimum to download an existing file
daysToNotDownload=0.5

#SQlite databse with the information of the datasets downloaded from Eurostat
#estatInfo='\\\\s-empl-py-stat1\\eurostat$\\Data\\estatInfo.db'

#Sync with the server G drive: active in local, inactive in server
syncActive=False


logFile='eurostat_info.csv'

#Local configuration
root_path='H:\\Data'
path='H:\\Data\\standard\\tsv\\'
csv_path='H:\\Data\\standard\\csv\\'
stacked_path='H:\\Data\\standard\\stacked\\'
stacked_q_path='H:\\Data\\standard\\stacked_q\\'
calculated_path='H:\\Data\\non_standard\\calculated\\'
original_path='H:\\Data\\non_standard\\original\\'
merged_path='H:\\Data\\merged\\'
dwh_path='H:\\Data\\non_standard\\dwh_format\\'

#Configuration for test W10
#root_path='C:\\Users\\arranda\\Data'
#path='C:\\Users\\arranda\\Data\\standard\\tsv\\'
#csv_path='C:\\Users\\arranda\\Data\\standard\\csv\\'
#stacked_path='C:\\Users\\arranda\\Data\\standard\\stacked\\'
#stacked_q_path='C:\\Users\\arranda\\Data\\standard\\stacked_q\\'
#calculated_path='C:\\Users\\arranda\\Data\\non_standard\\calculated\\'
#original_path='C:\\Users\\arranda\\Data\\non_standard\\original\\'
#merged_path='C:\\Users\\arranda\\Data\\merged\\'


#Network configuration
#catalogue path
root_path_n='G:\\F\\F4\\04 Data and tools\\catalogues\\'
reports_path_n='G:\\F\\F4\\04 Data and tools\\Reports\\'


