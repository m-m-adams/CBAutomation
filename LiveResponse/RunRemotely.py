import time
import os
import codecs 
from cbapi.response import CbEnterpriseResponseAPI, Sensor, SensorGroup

class RunRemotely(object):
    def __init__(self, HostName, ToolName='', Commandline='',code='UTF-8', OutputDir='Results', OutputExtension='.csv', remove=True, use_existing=False):
            self.HostName = HostName
            self.Tool = ToolName
            self.ToolName=os.path.basename(ToolName)
            self.LocalPath=ToolName
            self.Commandline=Commandline
            self.OutputDir=OutputDir
            self.OutputExtension=OutputExtension
            self.code=code
            self.remove=remove
            self.use_existing=use_existing
            
            self.remotedir=r'C:\Windows\CarbonBlack\Tools'
            self.remotepath=self.remotedir+"\\"+self.ToolName
            self.outputfile=os.path.join(OutputDir,HostName+self.OutputExtension)

            
    # sensor_id = 150  # Use this to define the sensor ID in the script, rather than using input
    def Run (self, session):

        
        if self.Tool.endswith('.ps1'):
            command='powershell.exe -executionpolicy bypass '+self.remotepath+self.Commandline
        elif self.Tool.endswith('.exe'):
            command=self.remotepath+' '+self.Commandline
        elif self.Tool == '':
            command=self.Commandline
        #print(localpath,remotedir,remotepath,Commandline,outputfile)
        
        print(self.Tool)
        try:
            if self.Tool != '':
                self.make_directory(session)


            print(self.HostName,'process is executing')
            print(command)
            output = session.create_process(command,\
                                            wait_for_output=True,remote_output_file_name=None,working_directory=None,wait_timeout=3600,wait_for_completion=True)

            print(self.HostName,'process is finished')

            #retreive the file full of autoruns

            text = codecs.decode(output,encoding=self.code,errors='replace')
            if os.path.exists(self.outputfile):
                os.remove(self.outputfile)
            
            with open(self.outputfile,'w',encoding='utf-8') as f:
                for line in text:
                    f.write(line)

            print('wrote artifact file to disk for ', self.HostName)
            
            #clean up after ourselves
            if self.remove:
                session.delete_file(self.remotepath)

        except Exception as err:  # Catch potential errors
            print('[ERROR] Encountered: ' + str(err) + '\n[FAILURE] Fatal error caused exit!')  # Report error    
            print('unsuccessful execution on '+self.HostName)
        session.close()
        print("Session has been closed to hostname #" + self.HostName)
        
    def make_directory(self, session):
        try:
            session.create_directory(self.remotedir)

        except :
            pass  # Existed already        
        try:
            print('placing the file {} to {}'.format(self.LocalPath, self.remotepath))
            session.put_file(open(self.LocalPath, 'rb'), self.remotepath)

        except Exception:
            if not self.use_existing:
                session.delete_file(self.remotepath)
                session.put_file(open(self.LocalPath, 'rb'), self.remotepath)






