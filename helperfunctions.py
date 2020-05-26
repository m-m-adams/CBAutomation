##This file contains example functions built on the RunRemotely class
import time
import os
import codecs 
from RunRemotely import RunRemotely
from cbapi.response import CbEnterpriseResponseAPI, Sensor, SensorGroup

def RunAutoruns(Group):
    #tool to run ()
    tool=r'.\Tools\autorunsc.exe'
    #arguments to run the tool with
    args=r''' -accepteula -nobanner -a * -c -h -mv -s *"'''
    #encoding of the tools output. Most sysinternals are UTF8, autoruns is UTF16
    code='UTF-16'
    #dir to write the files to
    output_dir='autorunsoutput'
    #extension to append on hostnames for file output
    output_ext='_autoruns.csv'

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    group=cb.select(SensorGroup).where("name:"+Group).first()

    for sensor in group.sensors:
        job=RunRemotely(sensor.hostname,tool,args,code,output_dir,output_ext)
        print(sensor.hostname)
        cb.live_response.submit_job(job.Run, sensor)
        print('job submitted')

def RunSigCheck(Group):
    #tool to run - must be in local dir
    tool='Tools/sigcheck.exe'
    #arguments to run the tool with
    args=r'''sigcheck.exe -accepteula -nobanner -c -e -h -s "C:\windows\system32"'''
    #encoding of the tools output. Most sysinternals are whatever the
    #windows default is on the remote computer, autoruns is UTF16
    # default can be checked with [System.Text.Encoding]::Default in powershell
    code='cp1252'
    #dir to write the files to
    output_dir='signatureoutput'
    #extension to append on hostnames for file output
    output_ext='_signatures.csv'

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    group=cb.select(SensorGroup).where("name:"+Group).first()

    for sensor in group.sensors:
        job=RunRemotely(sensor.hostname,tool,args,code,output_dir,output_ext)
        print(sensor.hostname)
        cb.live_response.submit_job(job.RunCode, sensor)
        print('job submitted')


def RunOSQuery(Group,Query):
    #Group to run on, Query to run, Dir to output to. Leave dir as empty string to send to stdout
    #tool to run - must be in local dir
    tool='Tools/osqueryi.exe'
    #arguments to run the tool with
    args="--json "+Query
    #encoding of the tools output.
    code='utf-8'
    #extension to append on hostnames for file output. enter empty string to send to stdout only
    output_ext='_query.json'
    output_dir="osqueryoutput"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    group=cb.select(SensorGroup).where("name:"+Group).first()

    for sensor in group.sensors:
        job=RunRemotely(sensor.hostname,tool,args,code,output_dir,output_ext, remove=False, use_existing=True)
        print(sensor.hostname)
        cb.live_response.submit_job(job.Run, sensor)
        print('job submitted')

def RunPowershell(Group):
    #script to run - must be in PSScripts dir
    script='PSScripts/get-autoruns.ps1'

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
        # def __init__(self, HostName, ToolName='', Commandline='',code='UTF-8', OutputDir='Results', OutputExtension='.csv', remove=True, use_existing=False):
        job=RunRemotely(sensor.hostname,script,code=code,OutputDir=output_dir,OutputExtension=output_ext)
        print(sensor.hostname)
        cb.live_response.submit_job(job.Run, sensor)
        print('job submitted')


if __name__ == '__main__':
    cb = CbEnterpriseResponseAPI()
    #group to search on
    Group='Default Group'
    RunOSQuery(Group, r'''"SELECT * FROM startup_items "''')
    #RunSigCheck(Group)