#%%
import time
import os
import codecs
from datetime import datetime, timedelta
import pandas as pd
import pprint
from cbapi.response import CbEnterpriseResponseAPI, Sensor, SensorGroup, Process


fields = ['process_name', 'cmdline', 'parent_name', 'modload_count','netconn_count',\
         'filemod_count','crossproc_count', 'childproc_count', 'group', 'hostname', \
         'last_update', 'start', 'id']


cb = CbEnterpriseResponseAPI()
query = cb.select(Process)
query = query.where("process_name:lsass.exe AND (crossproc_type:processopentarget or crossproc_type:remotethreadtarget)")
query = query.group_by('id')
query = query.min_last_update(datetime.today() - timedelta(days=100))
print('running query')
results = [process for process in query]
print('ran query with {} hits'.format(len(results)))

df = pd.DataFrame([process._info for process in results], columns=fields)

#%%

crossprocs =[]
for process in results:
    crossprocs = crossprocs + ([[process._info['process_name'],crossproc.source_path,\
                                crossproc.target_path, crossproc.type, crossproc.privileges,\
                                process._info['hostname'], process._info['id']]\
                                for crossproc in process.all_crossprocs() \
                                if crossproc.target_path.endswith('lsass.exe')])

crossproc_df = pd.DataFrame(crossprocs, columns=['process_name', 'source_path', 'target_path', \
                                                'type', 'privileges', 'hostname', 'id'])

#%%
grouped_by_process = crossproc_df.groupby(['source_path', 'privileges'], as_index=False)['id'].count()