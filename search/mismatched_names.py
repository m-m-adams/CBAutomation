#%%
import pandas as pd
from cbapi.response import CbEnterpriseResponseAPI, Sensor, SensorGroup, Process, Binary
#%%
cb=CbEnterpriseResponseAPI()

query = cb.select(Binary)
query = query.where('is_executable_image:true')
#This runs pretty much instantly on test with 10 000 binaries in server
bin_list = []

for binary in query:
        bin_list.append(binary._info)

bin_df = pd.DataFrame(bin_list)
bin_df = bin_df.explode('observed_filename')
#%%

grouped_by_name = bin_df.groupby('observed_filename')['md5', 'digsig_publisher','internal_name'].nunique()