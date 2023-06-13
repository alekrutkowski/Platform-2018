# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 15:40:45 2021

@author: franfab
"""

import pandas as pd
from config.parameters import *

myCatalogue_name='catalogue - SPPM_dashboard.csv'
significances_file='significances2022_Aug.csv'
estatSignificances=pd.read_csv(reports_path_n + 'SPPM Dashboard/config/' + significances_file)
dashboard_merged='SPPM_dashboard'
dashboard_final_file='dashboard_2022_Aug.xlsx'

country_profile_final_file='dashboard_country_profile_2022_Aug.xlsx'

#refYear???
