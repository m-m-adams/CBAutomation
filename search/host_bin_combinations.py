#%%
import pandas as pd
import numpy as np
import math
import pytz
from datetime import datetime, timedelta
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import IsolationForest
from cbapi.response import CbEnterpriseResponseAPI, Sensor, SensorGroup, Process, Binary

def trim_hostname(hostname):
    return hostname.split('|')[0].upper()

def list_to_dict(ls):
    return dict((item,1) for item in ls)

def recent_checkins():
    sensor_list=[]
    for sensor in sensors:
        if sensor.last_update > pytz.utc.localize(datetime.today()- timedelta(days=10)):
            #exclude the deployed server group, search them seperately later
            if sensor.group.id != 33: 
                sensor_list.append(sensor.computer_name.upper())
    return sensor_list
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
# produce a list of unique host/binary combinations. 
bin_df_hosts = bin_df.explode('endpoint')

# filter list to only binaries which are unsigned and on less than 60 hosts (arbitary)
bin_df_hosts = bin_df_hosts.loc[bin_df_hosts['signed'] != 'Signed']
bin_df_hosts = bin_df_hosts.loc[bin_df_hosts['host_count'] < 60]

# (convert into a df of hostname : list of binaries by both filename and md5
host_binaries = bin_df_hosts[['md5', 'endpoint']].groupby('endpoint').aggregate(lambda x: list(x))
host_filenames = bin_df_hosts[['observed_filename', 'endpoint']].groupby('endpoint').aggregate(lambda x: list(x))

# make a sensor query to only get hosts which have checked in within 10 days

host_binaries['hostname'] = host_binaries.index.map(trim_hostname)
sensors = cb.select(Sensor)

sensor_list = recent_checkins()
host_binaries = host_binaries[host_binaries['hostname'].isin(sensor_list)]

#%%
# convert the dataframe to an np matrix with host rows and md5 columns
# 1 corresponds to match, 0 is no match

host_binaries['md5'] = host_binaries['md5'].map(list_to_dict)

v = DictVectorizer(sparse=False)
host_binary_observations = v.fit_transform(host_binaries['md5'])
labels = v.get_feature_names()
hosts = host_binaries.index

#%%
#take hamming distance - in this case is the number of different binaries
hd = (2 * np.inner(host_binary_observations-0.5, 0.5-host_binary_observations) + host_binary_observations.shape[1] / 2)

# this is a matrix of correlation coefficients
corr = abs(np.corrcoef(host_binary_observations))

# make a new dataframe of host to their average correlation with all other hosts
# small values here are "more unique"
corr_means=pd.DataFrame(means, index=labels).sort_values()

# add back in binary names as a reference for the analyst
corr_means = corr_means.join(host_filenames)

#%%
