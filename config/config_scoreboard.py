# -*- coding: utf-8 -*-
"""
Created on Thu Aug  25th  2016

@author: badeape
"""

import os
import os.path
from os import path
import shutil

CtryList=['AT','BE','BG','CY','CZ','DE','DK','EE','EL','ES','FI','FR','HR','HU','IE','IT','LT','LU','LV','MT','NL','PL','PT','RO','SE','SI','SK']
EAList=['AT','BE','CY','DE','EE','EL','ES','FI','FR','IE','IT','LT','LU','LV','MT','NL','PT','SI','SK']
AggList=['EU27_2020','EA19']
AggNWList=['EUnw','EAnw']
#CompositeInd=['ID74']
ExCtryList=['AT','BE','BG','CY', 'CZ','DE','DK','EE','EL','ES','FI','FR','HR','HU','IE','IT','LT','LU','LV','MT','NL','PL','PT','RO','SE','SI','SK','EU27_2020','EA19']
ListSex=['T','F','M']

JER_catalogue='catalogue - JER Scoreboard.csv'
JER_catalogue_q='catalogue - JER Scoreboard_quarterly.csv'

basicpath = 'U:\\04 Data and tools\\Reports\\scoreboard\\2022.12.22\\'
localpath = basicpath + 'output\\'
checkpath = basicpath + 'checks\\'

#create subfolders

if path.exists(basicpath):
   print("")
else:
   os.mkdir(basicpath)
   os.mkdir(basicpath + 'output')
   os.mkdir(basicpath + 'dissemination')
   shutil.copy('U:\\04 Data and tools\\Reports\\scoreboard\\Countries_ranking.csv',localpath)

#add here a line asking for whether it is yearly or quarterly and changes the extraction file name accordingly
extractionFile='JER_scoreboard_data.csv'

