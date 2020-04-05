# KnockoffOSQuery
Abusing the CB live response API
1. This requires python 3. If you're on windows, install python3 (and remove 2 because it's deprecated) and do the module imports with pip. If you're on linux, install python3 and then do the imports with pip3. Keep python2 because it's probably a dependency for something.

2. Install dependencies:
pip install numpy  
repeat for scipy, pandas, cbapi, seaborn, matplotlib

3. Download these scripts to a folder, including the scriptoutput folder and .carbonblack

4. Rename the folder 'carbonblack' to '.carbonblack', then edit the api token. It's in .carbonblack\credentials.response. Replace YOUR_API_TOKEN with your api token.

5. The script RunEXEremotely.py is used to upload and run an executable. 
At the bottom of the script you feed it a name of the local tool to run, the directory name to output the results too, and an output extension to add to the filename. It expects to find the tool in the "tools" folder. It uploads the tool to carbonblack\tools on the remote machine, runs it with the given commands, writes stdout to $outputdir\$hostname_$extension, and then deletes the tool from the remote machine.

6. The script RunOSQuery is used to send queries into osqueryi. It uploads the copy of osqueryi from the tools directory to carbonblack/tools on the remote machine if it isn't already present, then runs the given command and either returns results to stdout or to disk.

6. The combination scripts are used find how frequently each entry occurs in the group. Things that are only on one or two machines are suspicious, but could also just indicate that the machine is behind on patching (expecially for sigcheck)

Don't use the ArtifactCapturePSJob script if there are computers on your network running powershell v1. It requires powershell 3 to run and v4 or higher to properly verify signatures. If yu run it on earlier versions, you'll have ~2000 hits as it's not possible to exlcude operating system core functions without verifying signatures.



