import os
import numpy as np
import pandas as pd


#ColumnNames=['Path','Item','Category','Value','ImagePath','Size','LastWriteTime','Version MD5','SHA1','SHA256','Signed','IsOSBinary','Publisher']
base_path='scriptoutput\\'


AutorunMatrix=pd.DataFrame(data=None)
for file in os.listdir(base_path):
    if file.lower().endswith('_signatures.csv'):
        NewDF=pd.read_csv(base_path+file,sep=",",encoding="ansi")
        NewDF['HostName']=file[:-11]
        AutorunMatrix=pd.concat([AutorunMatrix,NewDF], ignore_index=True)
#print(AutorunMatrix)
AutorunMatrix.to_csv('CombinedSignatures.csv',index=False)

ModdedMatrix=AutorunMatrix.drop(['Date','SHA1','HostName','Product Version','File Version','Machine Type', 'PESHA1','PESHA256','IMP'],axis=1)


ModdedMatrix = (ModdedMatrix.fillna('')\
      .groupby(ModdedMatrix.columns.tolist()).apply(len)\
      .rename('group_count')\
      .reset_index()\
      .replace('',np.nan)\
      .sort_values(by = ['Publisher','group_count'], ascending = False))
ModdedMatrix.to_csv('CountedSignatures.csv',index=False)
