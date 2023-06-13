# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from pandas import Series, DataFrame
from config.parameters import *

#define source and destination paths if different from "original" and "calculated". In that case, change the reference in the formulas
#source_path = 'H:\\Data\\non_standard\\original\\'
#destination_path = 'H:\\Data\\non_standard\\calculated\\'

#save the data sheet from the original Excel to CSV
df = pd.read_csv(original_path + 'Job_find_sep_data.csv')

finding = df[['cn_code', 'quarter', 'Job finding rates']]
separation = df[['cn_code', 'quarter', 'Job separation rates']]

finding.columns = ['geo', 'year', 'value_n']
separation.columns = ['geo', 'year', 'value_n']

finding['indicator'] = 'finding'
separation['indicator'] = 'separation'

findsep = pd.concat([finding, separation], ignore_index=True)
findsep = findsep.replace(['EU', 'EA'], ['EU27_2020', 'EA19'])

findsep.to_csv(calculated_path + 'find_sep_rate.csv', index=False)