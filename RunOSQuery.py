import time
import os
import json
from cbapi.response import CbEnterpriseResponseAPI, Sensor, SensorGroup

cb = CbEnterpriseResponseAPI()

class RunOsQueryRemotely(object):
    def __init__(self, HostName, ToolName, Commandline,encoding,OutputDir, OutputExtension):
            self.HostName = HostName
            self.ToolName=ToolName
            self.Commandline=Commandline
            self.OutputDir=OutputDir
            self.OutputExtension=OutputExtension
            self.encoding=encoding
            
    # sensor_id = 150  # Use this to define the sensor ID in the script, rather than using input
    def RunOsQuery (self, session):
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
        encoding=self.encoding
        #print(localpath,remotedir,remotepath,Commandline,outputfile)
        try:
            print(HostName,'trying query')
            try:
                output = session.create_process(command,wait_for_output=True,remote_output_file_name=None,working_directory=None,wait_timeout=3600,wait_for_completion=True)
            except Exception:
                print(HostName,'uploading osquery and retrying')
                session.put_file(open(localpath, 'rb'), remotepath)
                output = session.create_process(command,wait_for_output=True,remote_output_file_name=None,working_directory=None,wait_timeout=3600,wait_for_completion=True)
            print(HostName,'finished query')

            text = output.decode(encoding)
            print('Query Result for Host'+HostName+':\n\n\n'+text)

            if OutputDir != "":
                if os.path.exists(outputfile):
                    with open(outputfile,'r') as f:
                        json_data=json.load(f)
                        print('found previous json data')
                        json_data.append(json.loads(text))
                    with open(outputfile,'w') as f:
                        json.dump(json_data,f)
                else:
                    with open(outputfile,'w') as f:
                            json.dump(json.loads(text),f)

                print('wrote result to disk for further processing', HostName)
            

        except Exception as err:  # Catch potential errors
            print('[ERROR] Encountered: ' + str(err) + '\n[FAILURE] Fatal error caused exit!')  # Report error    
            print('unsuccessful execution on '+HostName)
        print("Session has been closed to hostname #" + HostName)

##CODE STARTS HERE
def RunOSQuery(Group,Query,output_dir):
    #Group to run on, Query to run, Dir to output to. Leave dir as empty string to send to stdout
    #tool to run - must be in local dir
    tool='osqueryi.exe'
    #arguments to run the tool with
    args="--json "+Query
    #encoding of the tools output. Most of the time it will be ANSI, autoruns is UTF16
    code='utf-8'

    #extension to append on hostnames for file output. enter empty string to send to stdout only
    output_ext='_query.json'
    if output_dir!="":
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

    group=cb.select(SensorGroup).where("name:"+Group).first()

    for sensor in group.sensors:
        job=RunOsQueryRemotely(sensor.hostname,tool,args,code,output_dir,output_ext)
        print(sensor.hostname)
        cb.live_response.submit_job(job.RunOsQuery, sensor)
        print('job submitted')

#group to search on
Group='Default Group'
#RunAutoruns(Group)
#RunSigCheck(Group)
RunOSQuery(Group,r'''"SELECT * FROM startup_items "''',"osqueryoutput")
