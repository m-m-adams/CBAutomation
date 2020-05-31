from cbapi.response import CbEnterpriseResponseAPI, Sensor, SensorGroup, Process
from datetime import datetime, timedelta
import pandas as pd
fields = ['process_name', 'cmdline', 'parent_name', 'modload_count','netconn_count',\
         'filemod_count','crossproc_count', 'childproc_count', 'group', 'hostname', \
         'last_update', 'start', 'id']

def search_dataframe (cb, query_string, ndays=1):
    query = cb.select(Process)
    query = query.where(query_string)
    query = query.group_by('id')
    query = query.min_last_update(datetime.today() - timedelta(days=ndays))

    results = []
    for process in query:
        results.append(process)


    df = pd.DataFrame([process._info for process in results], columns=fields)
    return df, results