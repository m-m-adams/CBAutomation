#%%
import pandas as pd
import numpy as np
import math
import pytz
from datetime import datetime, timedelta
from sklearn.feature_extraction import DictVectorizer
from sklearn.neighbors import LocalOutlierFactor
from cbapi.response import CbEnterpriseResponseAPI, Sensor, SensorGroup, Process, Binary

def trim_hostname(hostname):
    return hostname.split('|')[0].upper()

def trim_filename(filenames):
    if  isinstance(filenames, str):
        return str(filenames.split('\\')[-1].upper())
    result = []
    for name in filenames:
        result.append(str(name.split('\\')[-1].upper()))
    return result

def list_to_dict(ls):
    return dict((el,1) for el in ls)

def recent_checkins():
    sensor_list=[]
    for sensor in sensors:
        if sensor.last_update > pytz.utc.localize(datetime.today()- timedelta(days=10)):
            #exclude the deployed server group, search them seperately later
            if sensor.group.id != 33: 
                sensor_list.append(sensor.computer_name.upper())
    return sensor_list

def find_common_features(hd):
    # make a list of binaries which are identical to a previous binary
    to_drop = []
    for i in range(len(hd[0,:])):
        distance_vector = hd[:max(i-1,0),i]
        matches = [i for i, e in enumerate(distance_vector) if e == 0]
        if matches:
            to_drop.append(i)
    return to_drop

def obs_to_logprobabilites(obs_matrix):
    for i in range(len(obs_matrix[0,:])):
        nhosts = len(obs_matrix[:,0])
        total = np.sum(obs_matrix[:,i])
        probability = np.log(total/nhosts)
        obs_matrix[:,i] *= probability


#%%
cb=CbEnterpriseResponseAPI()

query = cb.select(Binary)
query = query.where('is_executable_image:true').where('server_added_timestamp:[2020-04-01T23:59:59 TO *]')
#query = query.where('md5:9C80EEDD823FFA6CE9CCE22BCF1C427D')
#This runs pretty much instantly on test with 10 000 binaries in server
bin_list = []
for binary in query:
    bin_list.append(binary._info)
    

bin_df = pd.DataFrame(bin_list)


# produce a list of unique host/binary combinations. 
bin_df_hosts = bin_df.explode('endpoint')

# filter list to only binaries which are unsigned and on less than 60 hosts (arbitary)
bin_df_hosts = bin_df_hosts.loc[((bin_df_hosts['signed'] != 'Signed') & (bin_df_hosts['host_count'] < 50))]



# (convert into a df of hostname : list of binaries by both filename and md5
bin_df_hosts['observed_filename'] = bin_df_hosts['observed_filename'].map(trim_filename)
host_binaries = bin_df_hosts[['md5', 'endpoint']].groupby('endpoint').aggregate(lambda x: list(x))


host_filenames = bin_df_hosts[['observed_filename', 'endpoint']].groupby('endpoint').aggregate(lambda x: list(x))
host_filenames['observed_filename'] = host_filenames['observed_filename'].map(lambda x: set([item for sublist in x for item in sublist]))
# make a sensor query to only get hosts which have checked in within 10 days

host_binaries['hostname'] = host_binaries.index.map(trim_hostname)
sensors = cb.select(Sensor)

sensor_list = recent_checkins()
host_binaries = host_binaries[host_binaries['hostname'].isin(sensor_list)]


# convert the dataframe to an np matrix with host rows and md5 columns
# 1 corresponds to match, 0 is no match

host_binaries['md5'] = host_binaries['md5'].map(list_to_dict)

v = DictVectorizer(sparse=False)
host_binary_observations = v.fit_transform(host_binaries['md5'])
labels = v.get_feature_names()
hosts = host_binaries.index


#take hamming distance - in this case is the number of different binaries
hd = (2 * np.inner(host_binary_observations.T-0.5, 0.5-host_binary_observations.T) + host_binary_observations.T.shape[1] / 2)

# this is a matrix of correlation coefficients
corr = abs(np.corrcoef(host_binary_observations))

# make a new dataframe of host to their average correlation with all other hosts
# small values here are "more unique"
means = np.mean(corr, axis=1)
corr_means=pd.DataFrame(means, index=hosts)

# add back in binary names as a reference for the analyst
corr_means = corr_means.join(host_filenames)

 
# uncommon binaries have scores above -1
# clf = LocalOutlierFactor(n_neighbors=3)
# outlier_labels = clf.fit_predict(host_binary_observations.T)

# neighbor_distance = pd.DataFrame(clf.negative_outlier_factor_, index=labels)


to_drop = find_common_features(hd)


# remove binaries with a hit based on the hamming distance
more_unique = np.delete(host_binary_observations, to_drop, axis=1)

unique_binaries = [v for i, v in enumerate(labels) if i not in to_drop]


# go through the array and replace 1s with the binaries log frequency
obs_to_logprobabilites(more_unique)

host_probabilities = sum(more_unique.T)
   

host_probs = pd.DataFrame(host_probabilities, index=hosts)

host_probs = host_probs.join(host_filenames)

host_probs.to_csv('./output.csv')

