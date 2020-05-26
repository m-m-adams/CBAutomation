# Automated IR tasks
1. This requires python 3

2. Dependencies:
numpy, scipy, pandas, cbapi, seaborn, matplotlib

3. Download these scripts to a folder, including the scriptoutput folder and .carbonblack

4. Rename the folder 'carbonblack' to '.carbonblack', then edit the api token. It's in .carbonblack\credentials.response. Replace YOUR_API_TOKEN with your api token.

5. The RunRemotely class is used to upload and run exe or powershell tools. This can be used for IR or threat hunt scripts, compliance checks, running osquery, or whatever else. There's some examples in helperfunctions.py


7. The combination scripts are used find how frequently each entry occurs in the group. Things that are only on one or two machines are suspicious, but could also just indicate that the machine is behind on patching (expecially for sigcheck)

Don't use the get-autoruns script if there are computers on your network running powershell v1. It requires powershell 3 to run and v4 or higher to properly verify signatures. If yu run it on earlier versions, you'll have ~2000 hits as it's not possible to exclude operating system core functions without verifying signatures.



