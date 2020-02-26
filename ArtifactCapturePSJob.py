## ----------------------------------------------------------------------------------------------------------------------------------------
##	Python Artifact Collection Script for use with Carbon Black Enterprise Response
##      ArtifactPullCBClean.ps1 - https://github.com/Jrotenberger/Powershell-IR-Scripts/blob/master/ArtifactPullCBClean.ps1
##
##  Version 1.1
##      Changelog: Version 1.1- The ExecutionPolicy is no longer modified, but rather an  ExecutionPolicy bypass is performed. 5/28/2019
##                 Version 1.0- Initial release. 9/4/2016
##
##  This Powershell script is updated to follow the collection process modelled by Corey Harrell's
##  TR3Secure Data Collection Script: http://journeyintoir.blogspot.com/2013/09/tr3secure-data-collection-script.html and
##  https://code.google.com/p/jiir-resources/downloads/list
##
##	References
##		Malware Forensics: Investigating and Analyzing Malicious Code by Cameron H. Malin, Eoghan Casey, and James M. Aquilina
## 		Windows Forensics Analysis (WFA) Second Edition by Harlan Carvey
## 		RFC 3227 - Guidelines for Evidence Collection and Archiving http://www.faqs.org/rfcs/rfc3227.html
##		Dual Purpose Volatile Data Collection Script http://journeyintoir.blogspot.com/2012/01/dual-purpose-volatile-data-collection.html
##		Corey Harrell (Journey Into Incident Response)
##		Sajeev.Nair - Nair.Sajeev@gmail.com	Live Response Script Desktop
##
##		Other contributors are mentioned in the code where applicable
##
##	Copyright 2019 Jeff Rotenberger
##
## ----------------------------------------------------------------------------------------------------------------------------------------
##
##
## ----------------------------------------------------------------------------------------------------------------------------------------

## ----------------------------------------------------------------------------------------------------------------------------------------
## Set Target
## ----------------------------------------------------------------------------------------------------------------------------------------

import time
from cbapi.response import CbEnterpriseResponseAPI, Sensor, SensorGroup

cb = CbEnterpriseResponseAPI()


# sensor_id = 150  # Use this to define the sensor ID in the script, rather than using input
def GetAutoruns (session):
    try:
        try:
            session.create_directory('C:\Windows\CarbonBlack\Tools')
            print('created directory')        
        except Exception:
            pass  # Existed already
            print('directory already present')
        
        try:
            session.put_file(open('.\get-autoruns.ps1', 'rb'), 'C:\Windows\CarbonBlack\Tools\get-autoruns.ps1')
            print('created the powershell script')
        except Exception: #already there, we think something is on the box so don't trust it
            print('script already present')
            session.delete_file('C:\Windows\CarbonBlack\Tools\get-autoruns.ps1')
            session.put_file(open('.\get-autoruns.ps1', 'rb'), 'C:\Windows\CarbonBlack\Tools\get-autoruns.ps1')
            print('replaced the file')
        #run the powershell script and save stdout
        HostName=session.create_process(r'''powershell.exe $env:computername''')
        HostName=str(HostName).strip('b')
        HostName=HostName[1:-5]
        print(HostName)
        #CbLRSessionBase.create_process(command_string,wait_for_output=True,remote_output_file_name=None,working_directory=None,wait_timeout=30,wait_for_completion=True)
        output = session.create_process(r'''powershell.exe -ExecutionPolicy Bypass "C:\Windows\CarbonBlack\Tools\get-autoruns.ps1"''',\
                                        wait_for_output=True,remote_output_file_name=None,working_directory=None,wait_timeout=3600,wait_for_completion=True)
        print('[SUCCESS] Script execution successful. Navigate to destination location for artifacts.')
        print('[DEBUG] Script Output:\n\n', output)


        #retreive the file full of autoruns
        #autoruns=session.get_file(r'C:\Windows\CarbonBlack\Tools\autoruns.csv')
        #print('grabbed the artifact file')
        
        f=open('scriptoutput\\'+str(HostName)+'_autoruns.csv','wb')
        f.write(output)
        f.close()

        print('wrote artifact file to disk')
        
        #clean up after ourselves
        session.delete_file('C:\Windows\CarbonBlack\Tools\get-autoruns.ps1')
        print('deleted powershell script')
    except Exception as err:  # Catch potential errors
        print('[ERROR] Encountered: ' + str(err) + '\n[FAILURE] Fatal error caused exit!')  # Report error    

    session.close()
    print("[INFO] Session has been closed to hostname #" + HostName)


group=cb.select(SensorGroup).where("name:R2-SW").first()

for sensor in group.sensors:
    cb.live_response.submit_job(GetAutoruns, sensor)
