import time
import os
import codecs 
from cbapi.response import CbEnterpriseResponseAPI, Sensor, SensorGroup

cb = CbEnterpriseResponseAPI()

class RunExeRemotely(object):
    def __init__(self, HostName, ToolName, Commandline,code,OutputDir, OutputExtension):
            self.HostName = HostName
            self.ToolName=ToolName
            self.Commandline=Commandline
            self.OutputDir=OutputDir
            self.OutputExtension=OutputExtension
            self.code=code
            
    # sensor_id = 150  # Use this to define the sensor ID in the script, rather than using input
    def RunCode (self, session):
        HostName=self.HostName
        Tool=self.ToolName
        Commandline=self.Commandline

        localpath=os.path.join('Tools',Tool)
        remotedir=r'C:\Windows\CarbonBlack\Tools'
        remotepath=remotedir+"\\"+Tool

        Output=self.OutputExtension
        OutputDir=self.OutputDir
        outputfile=os.path.join(OutputDir,(HostName+Output))
        command=remotepath+" "+Commandline
        code=self.code
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
            print(HostName,'tool is executing')
            #CbLRSessionBase.create_process(command_string,wait_for_output=True,remote_output_file_name=None,working_directory=None,wait_timeout=30,wait_for_completion=True)
            output = session.create_process(command,\
                                            wait_for_output=True,remote_output_file_name=None,working_directory=None,wait_timeout=3600,wait_for_completion=True)
            #print('[SUCCESS] Script execution successful. Navigate to destination location for artifacts.')
            #print('[DEBUG] Script Output:\n\n', output)
            print(HostName,'tool is finished')

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

##CODE STARTS HERE
def RunAutoruns(Group):
    #tool to run - must be in local dir
    tool='autorunsc.exe'
    #arguments to run the tool with
    args=r'''-accepteula -nobanner -a * -c -h -mv -s *"'''
    #encoding of the tools output. Most sysinternals are UTF8, autoruns is UTF16
    code='UTF-16'
    #dir to write the files to
    output_dir='scriptoutput'
    #extension to append on hostnames for file output
    output_ext='_autoruns.csv'

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    group=cb.select(SensorGroup).where("name:"+Group).first()

    for sensor in group.sensors:
        job=RunExeRemotely(sensor.hostname,tool,args,code,output_dir,output_ext)
        print(sensor.hostname)
        cb.live_response.submit_job(job.RunCode, sensor)
        print('job submitted')

def RunSigCheck(Group):
    #tool to run - must be in local dir
    tool='sigcheck.exe'
    #arguments to run the tool with
    args=r'''-accepteula -nobanner -c -e -h -s "C:\windows\system32"'''
    #encoding of the tools output. Most sysinternals are whatever the
    #windows default is on the remote computer, autoruns is UTF16
    # default can be checked with [System.Text.Encoding]::Default in powershell
    code='cp1252'
    #dir to write the files to
    output_dir='scriptoutput'
    #extension to append on hostnames for file output
    output_ext='_signatures.csv'

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    group=cb.select(SensorGroup).where("name:"+Group).first()

    for sensor in group.sensors:
        job=RunExeRemotely(sensor.hostname,tool,args,code,output_dir,output_ext)
        print(sensor.hostname)
        cb.live_response.submit_job(job.RunCode, sensor)
        print('job submitted')


#group to search on
Group='Default Group'
RunAutoruns(Group)
#RunSigCheck(Group)

