import time
import os
import codecs 
from cbapi.response import CbEnterpriseResponseAPI, Sensor, SensorGroup

cb = CbEnterpriseResponseAPI()

class RunExeRemotely(object):
    def __init__(self, HostName,scriptname,code,OutputDir, OutputExtension):
            self.HostName = HostName
            self.scriptname=scriptname
            self.OutputDir=OutputDir
            self.OutputExtension=OutputExtension
            self.code=code
            
    # sensor_id = 150  # Use this to define the sensor ID in the script, rather than using input
    def RunCode (self, session):
        HostName=self.HostName
        script=self.scriptname

        localpath=os.path.join('PSScripts',script)
        remotedir=r'C:\Windows\CarbonBlack\Tools'
        remotepath=remotedir+"\\"+script

        Output=self.OutputExtension
        OutputDir=self.OutputDir
        outputfile=os.path.join(OutputDir,HostName+Output)
        command=r"powershell.exe "+remotepath+" -executionpolicy bypass"
        code=self.code
        print(command)
        try:
            try:
                session.create_directory(remotedir)      
            except Exception:
                pass  # Existed already        
            try:
                session.put_file(open(localpath, 'rb'), remotepath)
            except Exception: #already there, we think something is on the box so don't trust it
                session.delete_file(remotepath)
                session.put_file(open(localpath, 'rb'), remotepath)

            #run the powershell script and save stdout
            print(HostName,'tool is executing')
            output = session.create_process(command,\
                                            wait_for_output=True,remote_output_file_name=None,working_directory=None,wait_timeout=600,wait_for_completion=True)
            #print('[SUCCESS] Script execution successful. Navigate to destination location for artifacts.')
            #print('[DEBUG] Script Output:\n\n', output)
            #Bypass=session.create_process('powershell.exe Set-ExecutionPolicy -executionpolicy restricted -scope currentuser')

            #retreive the file full of autoruns
            #autoruns=session.get_file(r'C:\Windows\CarbonBlack\Tools\autoruns.csv')
            #print('grabbed the artifact file')
            text = codecs.decode(output,encoding=code,errors='replace')
            print('converted to text')
            if os.path.exists(outputfile):
                os.remove(outputfile)
            
            with open(outputfile,'w',encoding='utf-8') as f:
                for line in text:
                    f.write(line)

            print('wrote artifact file to disk for ', HostName)
            
            #clean up after ourselves
            session.delete_file(remotepath)

        except Exception as err:  # Catch potential errors
            print('[ERROR] Encountered: ' + str(err) + '\n[FAILURE] Fatal error caused exit!')  # Report error    
            print('unsuccessful execution on '+HostName)
        #session.close()
        print("Session has been closed to hostname #" + HostName)

##code starts here

def RunPowershell(Group):
    #script to run - must be in PSScripts dir
    script='get-autoruns.ps1'

    #encoding of the tools output. cp1252 is the windows default
    # default can be checked with [System.Text.Encoding]::Default in powershell
    code='cp1252'
    #dir to write the files to
    output_dir='powershelloutput'
    #extension to append on hostnames for file output
    output_ext='_psautoruns.csv'

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    group=cb.select(SensorGroup).where("name:"+Group).first()

    for sensor in group.sensors:
        job=RunExeRemotely(sensor.hostname,script,code,output_dir,output_ext)
        print(sensor.hostname)
        cb.live_response.submit_job(job.RunCode, sensor)
        print('job submitted')


#group to search on
Group='Default Group'
RunPowershell(Group)

