# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 18:50:47 2019

@author: franfab
"""

from formula_engine.engine_v2 import *
from util.tools import *
from util.catalogues import *

def calculateAROPthreshold():
    download_and_stack(['ilc_li01','prc_hicp_aind'])
    for child in ['A1','A2_2CH_LT14']:
        ilc_li01=pd.read_csv(stacked_path+'ilc_li01.csv')
        #IN principle we use NAC to claculate the change but there are countries with broken series due to the transition to Euro
        # we need to combine the two groups in a single one
        # Fabio's update 11/6: the break in series seems to be solved for CY and SK, not for LT
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

#if SPPM test works ok delete this, otherwise put it back in call_catalogue.py
#def calculateAROPthreshold():
#    download_and_stack(['ilc_li01','prc_hicp_aind'])
#    for child in ['A1','A2_2CH_LT14']:
#        ilc_li01=pd.read_csv(stacked_path+'ilc_li01.csv')
#        #IN principle we use NAC to claculate the change but there are countries with broken series due to the transition to Euro
#        # we need to combine the two groups in a single one
#        # Fabio's update 11/6: the break in series seems to be solved for CY and SK, not for LT
#        ilc_li01_a=ilc_li01[(~ilc_li01.geo.isin(['CY','SK','LT']))&(ilc_li01.currency=='NAC')&(ilc_li01.hhtyp==child)&(ilc_li01.indic_il=='LI_C_MD60')]
#        ilc_li01_b=ilc_li01[(ilc_li01.geo.isin(['CY','SK','LT']))&(ilc_li01.currency=='EUR')&(ilc_li01.hhtyp==child)&(ilc_li01.indic_il=='LI_C_MD60')]
#        ilc_li01_final=ilc_li01_a.append(ilc_li01_b)
#        
#        prc_hicp_aind=pd.read_csv(stacked_path+'prc_hicp_aind.csv')
#        prc_hicp_aind=prc_hicp_aind[(prc_hicp_aind.coicop=='CP00')&(prc_hicp_aind.unit=='INX_A_AVG')]
#        #Decalate 1 year to deflate the income year of SILC
#        prc_hicp_aind['year']=prc_hicp_aind['year']+1
#        
#        merged=pd.merge(ilc_li01_final, prc_hicp_aind, on=['geo','year'])
#        merged['value_n']=100*merged['value_n_x']/merged['value_n_y']
#        merged.to_csv(calculated_path+'real_pov_threshold_'+child+'.csv')