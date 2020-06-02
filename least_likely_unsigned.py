#%%
import pandas as pd
import numpy as np
import math
from cbapi.response import CbEnterpriseResponseAPI, Sensor, SensorGroup, Process, Binary

    
#%%
cb=CbEnterpriseResponseAPI()

query = cb.select(Binary)
query = query.where('is_executable_image:true')
#query = query.where('md5:9C80EEDD823FFA6CE9CCE22BCF1C427D')
#This runs pretty much instantly on test with 10 000 binaries in server
bin_list = []
for binary in query:
    bin_list.append(binary._info)
    

bin_df = pd.DataFrame(bin_list)

#%%
max_count = bin_df['host_count'].max()

#calculate log probabilities of how likely all binaries are (low scores are rarer)
bin_df['freq_score'] = np.log(bin_df['host_count'] / 2000)


bin_df_hosts = bin_df.explode('endpoint')

host_likelihood = bin_df_hosts[bin_df_hosts['signed'] != 'Signed'].groupby('endpoint')['freq_score'].sum().sort_values()



