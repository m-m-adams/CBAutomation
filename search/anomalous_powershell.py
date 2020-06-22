#%%

import pandas as pd

from cbapi.response import CbEnterpriseResponseAPI
from search.searchfunctions import process_search_dataframe
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors

def get_silhouette_scores (df, kmin, kmax):
    sil = {}
    for k in range(kmin, kmax+1, (kmax-kmin)//10):
      kmeans = MiniBatchKMeans(n_clusters = k).fit(df)
      labels = kmeans.labels_
      score = silhouette_score(df, labels, metric = 'euclidean')
      sil[k]=score
      print(k, score)
    return sil
    
def find_common_features(corr):
    # make a list of binaries which are identical to a previous binary
    to_drop = []
    for i in range(len(corr[0,:])):
        distance_vector = corr[:max(i-1,0),i]
        matches = [i for i, e in enumerate(distance_vector) if e > 0.5]
        if matches:
            to_drop.append(i)
    return to_drop

def df_to_table(df, writer, hostname):
    df.to_excel(writer, sheet_name=hostname, index=False)
    worksheet = writer.sheets[hostname]
    col_names = [{'header': col_name} for col_name in df.columns]
    worksheet.add_table(0, 0, df.shape[0], df.shape[1], {
        'columns': col_names,
        # 'style' = option Format as table value and is case sensitive 
        # (look at the exact name into Excel)
        'style': 'Table Style Medium 10'
    })

#%%
cb=CbEnterpriseResponseAPI()
powershell_df, processes = process_search_dataframe(cb, 'process_name:powershell.exe -cmdline:Get-WinEvent', 100)

powershell_df.set_index('id', inplace=True)

powershell_df.to_csv('powershell10June.csv')
#%%
powershell_df = pd.read_csv('powershell10June.csv')
#%%
powershell_df = powershell_df.groupby(powershell_df.index).first()

# encode the cmdline and usernames to a one hot tokenized matrix, then add back in the count features

usr_vectorizer = CountVectorizer(token_pattern=r"[\w\.-]+")

tokenized_user = usr_vectorizer.fit_transform(powershell_df['username'])
user_df = pd.DataFrame.sparse.from_spmatrix(tokenized_user, index=powershell_df.index, columns=usr_vectorizer.get_feature_names())
cmd_vectorizer = CountVectorizer(token_pattern=r"[\w\.-]+")

tokenized_cmd = cmd_vectorizer.fit_transform(powershell_df['cmdline'])

feature_df = pd.DataFrame.sparse.from_spmatrix(tokenized_cmd, index=powershell_df.index, columns=cmd_vectorizer.get_feature_names())

feature_df = feature_df.merge(user_df, left_index=True, right_index=True)

feature_df = feature_df.merge(powershell_df.loc[:, ['modload_count', 'childproc_count', 'netconn_count', 'crossproc_count']], left_index=True, right_index=True)


#%%

# scale the feature matrix

ss = StandardScaler()
ss.fit(feature_df)
data_transformed = ss.transform(feature_df)

#%%

kmax = 500
kmin = 100

sil = get_silhouette_scores(data_transformed, kmin, kmax)

lastscore = 0
lastk=0
for k, score in sil.items():
    if score < lastscore:
        lastk = k
        break
#%% KMeans
# technically suboptimal but kmodes lacks a C implementation and runtime is terrible
        
        
clustering = KMeans(n_clusters=lastk).fit_predict(feature_df, categorical=list(range(0,864)))
labels = clustering.labels_  

powershell_df['label'] = labels

powershell_df.to_csv('kprototypes_clustered_powershell.csv')



fields = ['process_name', 'cmdline', 'parent_name', 'modload_count','netconn_count',\
         'filemod_count','crossproc_count', 'childproc_count', 'group', 'username', 'hostname', \
         'last_update', 'start', 'id']

label_groups = powershell_df.groupby('label')['cmdline'].count().sort_values()
label_df = label_groups.to_frame(name='group_size')
sized_df = powershell_df.merge(label_df, on='label')

normalized_clustered = pd.read_csv('kmeans_clustered_powershell.csv')



fields = ['process_name', 'cmdline', 'parent_name', 'modload_count','netconn_count',\
         'filemod_count','crossproc_count', 'childproc_count', 'group', 'username', 'hostname', \
         'last_update', 'start', 'id']

label_groups = powershell_df.groupby('label')['cmdline'].count().sort_values()
label_df = label_groups.to_frame(name='group_size')
sized_df = powershell_df.merge(label_df, on='label')

unique_executions = sized_df.loc[sized_df['group_size'] < 15][['group_size', 'label']+fields]

unique_executions['link'] = "https://eedr.forces.mil.ca:8443/#/analyze/"+unique_executions['id']

with pd.ExcelWriter("unique_executions.xlsx") as writer:
    df_to_table(unique_executions, writer, "unique_powershell")
    

#%% KNN anomalies
clf = NearestNeighbors(metric="hamming", n_neighbors=5, n_jobs=-1)       
clf.fit(feature_df)
dist, _ = clf.kneighbors(feature_df)

distances = dist[:,-1]

powershell_df['distance'] = distances
anomalies = powershell_df.sort_values(['distance'], ascending=False).head(100)

powershell_df.to_csv('KNN_powershell.csv')
