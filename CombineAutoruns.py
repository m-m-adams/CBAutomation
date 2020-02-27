import os
import numpy as np
import pandas as pd


def SubUsername(ImagePath):
    Folders=ImagePath.split('\\')
    if len(Folders)>2:
        if Folders[1]=='Users':
            Folders[2]='$Username'
        return '\\'.join(Folders)
    return ''

#ColumnNames=['Path','Item','Category','Value','ImagePath','Size','LastWriteTime','Version MD5','SHA1','SHA256','Signed','IsOSBinary','Publisher']
base_path='scriptoutput\\'


AutorunMatrix=pd.DataFrame(data=None)
for file in os.listdir(base_path):
    if file.lower().endswith('_autoruns.csv'):
        NewDF=pd.read_csv(base_path+file,sep=",",encoding="ansi")
        NewDF['HostName']=file[:-13]
        AutorunMatrix=pd.concat([AutorunMatrix,NewDF], ignore_index=True)
#print(AutorunMatrix)
AutorunMatrix.to_csv('CombinedAutoruns.csv',index=False)

ModdedMatrix=AutorunMatrix[['Category','Entry Location','Entry','Image Path','Launch String','Description','Signer','Company','MD5','SHA-256']]

ModdedMatrix['Image Path']=ModdedMatrix['Image Path'].map(lambda path:SubUsername(str(path)))

ModdedMatrix = (ModdedMatrix.fillna('')\
      .groupby(ModdedMatrix.columns.tolist()).apply(len)\
      .rename('group_count')\
      .reset_index()\
      .replace('',np.nan)\
      .sort_values(by = ['Category','group_count'], ascending = False))
ModdedMatrix.to_csv('CountedAutoruns.csv',index=False)
