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
            session.put_file(open('.\sigcheck.exe', 'rb'), 'C:\Windows\CarbonBlack\Tools\sigcheck.exe')
            print('created the powershell script')
        except Exception: #already there, we think something is on the box so don't trust it
            print('script already present')
            session.delete_file('C:\Windows\CarbonBlack\Tools\sigcheck.exe')
            session.put_file(open('.\sigcheck.exe', 'rb'), 'C:\Windows\CarbonBlack\Tools\sigcheck.exe')
            print('replaced the file')
        #run the powershell script and save stdout
        HostName=session.create_process(r'''powershell.exe $env:computername''')
        HostName=str(HostName).strip('b')
        HostName=HostName[1:-5]
        print(HostName)
        #CbLRSessionBase.create_process(command_string,wait_for_output=True,remote_output_file_name=None,working_directory=None,wait_timeout=30,wait_for_completion=True)
        output = session.create_process(r'''sigcheck.exe -accepteula -nobanner -c -s C:/windows/system32/''',\
                                        wait_for_output=True,remote_output_file_name=None,working_directory=None,wait_timeout=3600,wait_for_completion=True)
        print('[SUCCESS] Script execution successful. Navigate to destination location for artifacts.')
        print('[DEBUG] Script Output:\n\n', output)


        #retreive the file full of autoruns

        f=open('scriptoutput\\'+str(HostName)+'_sys32signatures.csv','wb')
        f.write(output)
        f.close()

        print('wrote artifact file to disk')
        
        #clean up after ourselves
        session.delete_file('C:\Windows\CarbonBlack\Tools\sigcheck.exe')
        print('deleted powershell script')
    except Exception as err:  # Catch potential errors
        print('[ERROR] Encountered: ' + str(err) + '\n[FAILURE] Fatal error caused exit!')  # Report error    

    session.close()
    print("[INFO] Session has been closed to hostname #" + HostName)


group=cb.select(SensorGroup).where("name:R2-SW").first()

for sensor in group.sensors:
    cb.live_response.submit_job(GetAutoruns, sensor)
