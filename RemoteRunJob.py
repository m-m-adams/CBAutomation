import time
import os
from cbapi.response import CbEnterpriseResponseAPI, Sensor, SensorGroup

cb = CbEnterpriseResponseAPI()

class RunCodeRemotely(object):
    def __init__(self, HostName, ToolName, Commandline,OutputDir, OutputExtension):
            self.HostName = HostName
            self.ToolName=ToolName
            self.Commandline=Commandline
            self.OutputDir=OutputDir
            self.OutputExtension=OutputExtension
            
    # sensor_id = 150  # Use this to define the sensor ID in the script, rather than using input
    def RunCode (self, session):
        HostName=self.HostName
        Tool=self.ToolName
        Commandline=self.Commandline

        localpath=Tool
        remotedir=r'C:\Windows\CarbonBlack\Tools'
        remotepath=remotedir+"\\"+Tool

        Output=self.OutputExtension
        OutputDir=self.OutputDir
        outputfile=OutputDir+'\\'+HostName+Output
        command=remotepath+" "+Commandline
        #print(localpath,remotedir,remotepath,Commandline,outputfile)
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
            #HostName=session.create_process(r'''powershell.exe $env:computername''')
            #HostName=str(HostName).strip('b')
            #HostName=HostName[1:-5]

            #CbLRSessionBase.create_process(command_string,wait_for_output=True,remote_output_file_name=None,working_directory=None,wait_timeout=30,wait_for_completion=True)
            output = session.create_process(command,\
                                            wait_for_output=True,remote_output_file_name=None,working_directory=None,wait_timeout=3600,wait_for_completion=True)
            #print('[SUCCESS] Script execution successful. Navigate to destination location for artifacts.')
            #print('[DEBUG] Script Output:\n\n', output)
            print(HostName,'tool is executing')

            #retreive the file full of autoruns
            #autoruns=session.get_file(r'C:\Windows\CarbonBlack\Tools\autoruns.csv')
            #print('grabbed the artifact file')


            if os.path.exists(outputfile):
                os.remove(outputfile)
            
            with open(outputfile,'wb') as f:
                f.write(output)

            print('wrote artifact file to disk for ', HostName)
            
            #clean up after ourselves
            session.delete_file(remotepath)

        except Exception as err:  # Catch potential errors
            print('[ERROR] Encountered: ' + str(err) + '\n[FAILURE] Fatal error caused exit!')  # Report error    

        #session.close()
        print("Session has been closed to hostname #" + HostName)

##CODE STARTS HERE
Group='Default Group'
tool='autorunsc.exe'
commands=r'''-accepteula -nobanner -a * -c -mv -s *"'''
output_dir='scriptoutput'
output_ext='_autoruns.csv'

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

group=cb.select(SensorGroup).where("name:"+Group).first()

for sensor in group.sensors:
    job=RunCodeRemotely(sensor.hostname,tool,commands,output_dir,output_ext)
    print(sensor.hostname)
    cb.live_response.submit_job(job.RunCode, sensor)
    print('job submitted')
