# KnockoffOSQuery
Abusing the CB live response API
1. This requires python 3. If you're on windows, install python3 (and remove 2 because it's deprecated) and do the module imports with pip. If you're on linux, install python3 and then do the imports with pip3. Keep python2 because it's probably a dependency for something.

2. Install dependencies:
pip install numpy  
repeat for scipy, pandas, cbapi, seaborn, matplotlib

3. Download these scripts to a folder, including the scriptoutput folder and .carbonblack

4. Rename the folder 'carbonblack' to '.carbonblack', then edit the api token. It's in .carbonblack\credentials.response. Replace YOUR_API_TOKEN with your api token.

5. Use the script RemoteRunJob.py
At the bottom of the script you feed it a name of the local tool to run, the directory name to output the results too, and an output extension to add to the filename. It uploads the tool to carbonblack\tools on the remote machine, runs it with the given commands, writes stdout to $outputdir\$hostname_$extension, and then deletes the tool from the remote machine.



6. Use CombineAutoruns to find how frequently each entry occurs in the range

Don't use the ArtifactCapturePSJob script if there are computers on your network running powershell v1. It requires powershell 3 or higher to properly verify signatures. If yu run it on powershell v1, you'll have ~2000 hits as it's not possible to exlcude operating system core functions without verifying signatures.



