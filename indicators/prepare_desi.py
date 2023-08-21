import pandas as pd
import numpy as np
import requests
from io import BytesIO
import os
from config.parameters import *

print('Downloading DESI.csv.zip ...')
req = requests.get('https://digital-agenda-data.eu/download/DESI.csv.zip')
print('Download completed.')

df = pd.read_csv(BytesIO(req.content),
                 compression='zip')
df = df[df.indicator == 'desi_conn']
df = df.pivot_table(index=["ref_area", "time_period"],
                    values="value",
                    aggfunc=np.sum)
df['value_n'] = df.value * 100
df = df.drop(columns=['value'])
df = pd.DataFrame(df.to_records())
df = df.rename(columns={"ref_area": "geo",
                        "time_period": "year"})
df.to_csv(os.path.join(calculated_dir, 'DESI_Connectivity.csv'))
print('DESI_Connectivity.csv' + ' has been saved in ' + calculated_dir)
