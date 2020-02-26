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

AutorunMatrix=pd.DataFrame(data=None)
for file in os.listdir():
    if file.lower().endswith('output.csv'):
        NewDF=pd.read_csv(file)
        NewDF['HostName']=file[:-10]
        AutorunMatrix=pd.concat([AutorunMatrix,NewDF], ignore_index=True)
#print(AutorunMatrix)
AutorunMatrix.to_csv('CombinedAutoruns.csv',index=False)

ModdedMatrix=AutorunMatrix[['Category','Path','Item','ImagePath','Signed','Publisher','SHA256']]

ModdedMatrix['ImagePath']=ModdedMatrix['ImagePath'].map(lambda path:SubUsername(str(path)))

ModdedMatrix = (ModdedMatrix.fillna('')\
      .groupby(ModdedMatrix.columns.tolist()).apply(len)\
      .rename('group_count')\
      .reset_index()\
      .replace('',np.nan)\
      .sort_values(by = ['group_count'], ascending = False))
ModdedMatrix.to_csv('ModdedAutoruns.csv',index=False)
