# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 09:22:23 2018

@author: badeape
"""

from util.download_data import *
from util.tools import *
#from util.jaf_utils import * 
outputFile='net_earn'
startYear=2001

# Read the file extrcated form ECFIN AMECO
earnings = pd.read_csv(original_path+'net_earnings_ECFIN.csv', na_values=[' na','na'], header=1,skipfooter=1)
earnings = earnings.set_index(['country', 'indicator', 'family_composition', 'earnings'])
earnings = earnings.stack()
earnings = earnings.reset_index()
earnings['indic']=earnings['family_composition'].map(str) +"."+earnings['earnings'].map(int).map(str)  
earnings = earnings.drop([ 'indicator', 'family_composition', 'earnings'],axis=1)
earnings.columns= ['geo','year','value_n','indicator'] 
c = earnings.copy()
c['file']=outputFile
c['flag']='' 
c['year']=c['year'].map(int)
c = c[c.year>startYear]

c=pd.DataFrame(c,columns=['year','geo','file','value_n','indicator','flag'])
c.to_csv(calculated_path+outputFile+'.csv',index=False, float_format='%.4f')
