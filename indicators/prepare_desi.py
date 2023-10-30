import pandas as pd
import numpy as np
import requests
from io import BytesIO
import os
from config.parameters import *

print('Downloading DESI.csv ...')
req = requests.get('https://digital-decade-desi.digital-strategy.ec.europa.eu/api/v1/chart-groups/desi-2022/facts/')
print('Download completed.')

df = pd.read_csv(BytesIO(req.content))
df = df[df.indicator == 'desi_conn']
df = df.pivot_table(index=["country", "period"],
                    values=["value","flags"],
                    aggfunc=lambda x: x) # np.sum
# df['value_n'] = df.value * 100    # already in percent
# df = df.drop(columns=['value'])
df = pd.DataFrame(df.to_records())
df = df.rename(columns={"country": "geo",
                        "period": "year",
                        "value": "value_n",
                        "flags": "flag"})
df['file'] = 'desi'
df = df[["geo","year","file","value_n","flag"]]
duplicate_mask = df.duplicated(subset=['geo', 'year'], keep=False)
has_duplicates = duplicate_mask.any()
if has_duplicates:
    print('[ERROR!] The columns "geo" and "year" do not uniquely identify the rows.')
    duplicate_rows = df[duplicate_mask]
    print(duplicate_rows)
df.to_csv(os.path.join(calculated_path, 'desi.csv'),
          index=False)
print('desi.csv' + ' has been saved in ' + calculated_path)
