import time
import os
import json
from cbapi.response import CbEnterpriseResponseAPI, Sensor, SensorGroup

cb = CbEnterpriseResponseAPI()

class RunShRemotely(object):
    def __init__(self, HostName, Commandline,OutputDir, OutputExtension):
            self.HostName = HostName
            self.Commandline=Commandline
            self.OutputDir=OutputDir
            self.OutputExtension=OutputExtension
            
    # sensor_id = 150  # Use this to define the sensor ID in the script, rather than using input
    def RunSh (self, session):
        HostName=self.HostName
        Commandline=self.Commandline
        Output=self.OutputExtension
        OutputDir=self.OutputDir
        outputfile=os.path.join(OutputDir,(HostName+Output))
        encoding='cp1252'
        #print(localpath,remotedir,remotepath,Commandline,outputfile)
        try:
            print(HostName,'trying command')
            output = session.create_process(Commandline,wait_for_output=True,remote_output_file_name=None,working_directory=None,wait_timeout=3600,wait_for_completion=True)
            print(HostName,'finished command')

            text = output.decode(encoding)
            print('Result for Host'+HostName+':\n\n\n'+text)

            if OutputDir != "":
                if os.path.exists(outputfile):
                    os.remove(outputfile)
                
                with open(outputfile,'w',encoding='utf-8') as f:
                    for line in text:
                        f.write(line)

                print('wrote result to disk for further processing', HostName)
            

        except Exception as err:  # Catch potential errors
            print('[ERROR] Encountered: ' + str(err) + '\n[FAILURE] Fatal error caused exit!')  # Report error    
            print('unsuccessful execution on '+HostName)
        print("Session has been closed to hostname #" + HostName)

##CODE STARTS HERE
def RunShell(Group,Command):
    #Group to run on, Query to run, Dir to output to. Leave dir as empty string to send to stdout
    #arguments to run the tool with
    args=Command
    #extension to append on hostnames for file output. enter empty string to send to stdout only
    output_ext='_result.json'
    output_dir="shelloutput"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    group=cb.select(SensorGroup).where("name:"+Group).first()

    for sensor in group.sensors:
        job=RunShRemotely(sensor.hostname,args,output_dir,output_ext)
        print(sensor.hostname)
        cb.live_response.submit_job(job.RunSh, sensor)
        print('job submitted')

#group to search on
Group='Default Group'
#RunAutoruns(Group)
#RunSigCheck(Group)
RunShell(Group,r'''powershell.exe import-module bitstransfer; get-bitstransfer -allusers|foreach {$_}|ConvertTo-csv -notypeinformation''')
