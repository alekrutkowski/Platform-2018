# -*- coding: utf-8 -*-
"""
Created on Mon May 25 22:42:20 2020

@author: franfab
"""

from formula_engine.engine_v2 import *
from util.tools import *
from util.catalogues import *
from indicators.AROP_threshold import *
from call_catalogue import *


calculateAROPthreshold()
sppm=anyCatalogue('catalogue - SPPM_annex.csv', 'SPPM_data')
download_and_stack(['spr_exp_gdp'])