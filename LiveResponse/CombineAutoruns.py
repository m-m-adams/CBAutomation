import os
import numpy as np
import pandas as pd
from pathlib import Path
import openpyxl
import re


def sub_username(ImagePath):
    ImagePath = str(ImagePath)
    Folders=ImagePath.split('\\')
    if len(Folders)>2:
        if Folders[1]=='Users':
            Folders[2]='$Username'
        return '\\'.join(Folders)
    return ''

def sub_sid(ImagePath):
    ImagePath = str(ImagePath)
    SID = re.search(r"S[_-]\d[_-]\d+[_-](\d+[_-]){1,14}\d+", ImagePath)
    if SID:
        return ImagePath.replace(SID.group(), 'user_sid')
    return ImagePath

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

#ColumnNames=['Path','Item','Category','Value','ImagePath','Size','LastWriteTime','Version MD5','SHA1','SHA256','Signed','IsOSBinary','Publisher']


def combine_count_autoruns(base_path, output, extension):
    with pd.ExcelWriter(os.path.join(base_path,output)) as writer:
        temp = pd.DataFrame({'data':[0,0,0]})
        temp.to_excel(writer, sheet_name='counted_autoruns')
        AutorunMatrix=pd.DataFrame(data=None)
        for file in os.listdir(base_path):
            
            if file.lower().endswith(extension) and Path(os.path.join(base_path,file)).stat().st_size<400000:
                try:
                    hostname = file[:-15]
                    NewDF=pd.read_csv(os.path.join(base_path,file),sep=",",encoding="ansi")
                    NewDF['HostName']=hostname
                    AutorunMatrix=pd.concat([AutorunMatrix,NewDF], ignore_index=True)
                    df_to_table(NewDF, writer, hostname)
                except pd.errors.ParserError:
                    print('error with file {}'.format(file))
        
        #ModdedMatrix=AutorunMatrix[['Category','Entry Location','Entry','Image Path','Launch String','Description','Signer','Company','MD5','SHA-256']]
        ModdedMatrix=AutorunMatrix[['Category','Path','Item','Value','ImagePath','Publisher','MD5','SHA256']]
        ModdedMatrix.loc[:,'ImagePath']=ModdedMatrix['ImagePath'].map(sub_username)
        ModdedMatrix.loc[:,'Path']=ModdedMatrix['Path'].map(sub_sid)
        ModdedMatrix.loc[:,'Item']=ModdedMatrix['Item'].map(sub_sid)
        
        ModdedMatrix = (ModdedMatrix.fillna('')\
              .groupby(ModdedMatrix.columns.tolist()).apply(len)\
              .rename('group_count')\
              .reset_index()\
              .replace('',np.nan)\
              .sort_values(by = ['Category','group_count'], ascending = False))
        df_to_table(ModdedMatrix, writer, 'counted_autoruns')


if __name__ == '__main__':
    base_path=r'pathtofolder'
    output = 'combined_psautoruns.xlsx'
    extension = '_psautoruns.csv'
    combine_count_autoruns(base_path, output, extension)
