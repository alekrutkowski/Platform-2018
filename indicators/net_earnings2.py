# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 16:54:55 2018

@author: badeape
"""

import numpy as np
from config.parameters import *
from util.download_data import * # David's tool
ExCtryList=['AT','BE','BG','CY', 'CZ','DE','DK','EE','EL','ES','FI','FR','HR','HU','IE','IT','LT','LU','LV','MT','NL','PL','PT','RO','SE','SI','SK','EU27_2020','EA19']
localpath = 'H:\\Data\\Net earnings\\'
startYear = 2002
startYear_Scoreboard = 2016
source = 'ECFIN'
outputFile='net_earn'
ratesFile='exchange_rates'

def calculate_average(group):
    group['average_pps'] = (group.pps+group.pps.shift(-1)+group.pps.shift(-2))/3
    return (group)

def calculate_change(group):
    group['change_NAC'] = 100*((group.earnings-group.earnings.shift(-1))/group.earnings.shift(-1))
    return (group)

def calculate_change1(group):
    group['change_real'] = 100*((group.real-group.real.shift(-1))/group.real.shift(-1))
    group['average_change'] = (group.change_real+group.change_real.shift(-1)+group.change_real.shift(-2))/3
    return (group)


allFiles=['earn_nt_net','prc_hicp_aind','prc_ppp_ind','ert_h_eur_a'] # These go to C:\Data\standard\stacked
download_and_stack(allFiles)

# Calculate net earnings taking account of exchange rates to correct for MS joining between 2002 and 2015
exchangeRate = pd.read_csv(calculated_path+ratesFile+'.csv')
net_earnings = pd.read_csv(calculated_path+outputFile+'.csv')
net_earnings = net_earnings[(net_earnings.geo.isin(ExCtryList))]
net_earnings = net_earnings[(net_earnings.year >=startYear)]
net_earnings['flag'] = net_earnings['flag'].replace(np.nan,'')
net_earnings=pd.merge(net_earnings,exchangeRate,on=['geo','year'])
net_earnings['value']=net_earnings['value_n_x']/net_earnings['value_n_y']
net_earnings = net_earnings[['geo','year','value','flag']]
net_earnings.columns=['geo','year','earnings','eflag']
net_earnings.to_csv(localpath+'net_earnings_NAC.csv',index=False, float_format='%.4f')

#exchange = pd.read_csv(stacked_path+'ert_h_eur_a.csv')

# Extrcat the HICP to be used in all calculations
HICP = pd.read_csv(stacked_path+'prc_hicp_aind.csv')
HICP = HICP[(HICP.coicop == 'CP00') & (HICP.unit == 'INX_A_AVG')]
HICP = HICP[(HICP.geo.isin(ExCtryList))]
HICP = HICP[(HICP.year >=startYear)]
HICP['flag'] = HICP['flag'].replace(np.nan,'')
HICP = HICP[['geo','year','value_n','flag']]
HICP.columns=['geo','year','HICP','iflag']
HICP.to_csv(localpath+'HICP.csv',index=False, float_format='%.4f')

# Extract PPPs to calculate net earnings in PPSs
PPP = pd.read_csv(stacked_path+'prc_ppp_ind.csv')
PPP = PPP[(PPP.ppp_cat=='GDP') & (PPP.na_item == 'PPP_EU27_2020')]
PPP = PPP[(PPP.geo.isin(ExCtryList))]
PPP = PPP[(PPP.year >=startYear)]
PPP['flag'] = PPP['flag'].replace(np.nan,'')
PPP = PPP[['geo','year','value_n','flag']]
PPP.columns=['geo','year','PPP','pflag']
PPP.to_csv(localpath+'PPP.csv',index=False, float_format='%.4f')

# Merge net earnings with HICP and PPP
table = pd.merge(HICP,PPP, on=['geo','year'])
table = pd.merge(table,net_earnings, on=['geo','year'])


# Calculate the real net earnings and net earnings in PPSs
# Then, calculate the change and averages
table['real'] = table.earnings/table.HICP*100
table['pps'] = table.earnings/table.PPP
table=table.groupby('geo').apply(calculate_change)       # % change for earnings in NAC
table=table.groupby('geo').apply(calculate_change1)      # % change for real net earnings and the 3 years average change
table=table.groupby('geo').apply(calculate_average)      # 3 year average for net earnings in PPSs

earnings=table[['geo','year','earnings','real','pps']]   # Contains net earnings in NAC, real and PPS
changes=table[['geo','year','change_NAC','change_real']] # Contains the two changes, in NAC and real
changes = changes[(changes.year >=startYear+1)]
averages=table[['geo','year','average_pps']]             # Contains the average net earnings in PPSs
averages=averages[(averages.year>=startYear+2)]
av_changes=table[['geo','year','average_change']]        # Contains the average change of net earnings real terms
av_changes=av_changes[(av_changes.year>=startYear+3)]

net_earnings=table[['geo','year','average_pps','average_change']]
net_earnings=net_earnings[(net_earnings.year>=startYear_Scoreboard)]
net_earnings['Group'] ='Fair working conditions'
net_earnings['IND_CODE'] ='ID74'
net_earnings['Indicator'] ='Net earnings'
net_earnings['Order'] =74
net_earnings['change'] ='pp'
net_earnings['sense'] ='pos'
net_earnings['type'] ='H'
net_earnings['flag'] =''
net_earnings['ychange_flag'] =''
net_earnings = net_earnings[['Group','IND_CODE','Indicator','Order','change','flag','geo','sense','type','average_pps','average_change','ychange_flag','year']] 
net_earnings.columns=['Group','IND_CODE','Indicator','Order','change','flag','geo','sense','type','value_n','ychange','ychange_flag','year']

earnings_level = table[['geo','year','average_pps']]
earnings_level.columns=['geo','year','value_n']

net_earnings.to_csv(calculated_path+'net_earnings.csv',index=False, float_format='%.4f') # Needed for ESTAT
earnings_level.to_csv(calculated_path+'earnings_level.csv',index=False, float_format='%.4f') # Needed for SCO and (?) ESTAT
table.to_csv(localpath+'table.csv',index=False, float_format='%.4f')
earnings.to_csv(localpath+'earnings.csv',index=False, float_format='%.4f')
changes.to_csv(localpath+'changes.csv',index=False, float_format='%.4f') # Needed for SCO
averages.to_csv(localpath+'average_pps.csv',index=False, float_format='%.4f')
av_changes.to_csv(localpath+'average_change.csv',index=False, float_format='%.4f')


