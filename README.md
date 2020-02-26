# KnockoffOSQuery
Abusing the CB live response API
1. This requires python 3. If you're on windows, install python3 (and remove 2 because it's deprecated) and do the module imports with pip. If you're on linux, install python3 and then do the imports with pip3. Keep python2 because it's probably a dependency for something.

2. Install dependencies:
pip install numpy  
repeat for scipy, pandas, cbapi, seaborn, matplotlib

3. Download these scripts to a folder, including the scriptoutput folder and .carbonblack

4. Rename the folder 'carbonblack' to '.carbonblack', then edit the api token. It's in .carbonblack\credentials.response. Replace YOUR_API_TOKEN with your api token.

5. Run job scripts, they write a bunch of csv files to scriptoutput

6. Use CombineAutoruns to find how frequently each entry occurs in the range

Don't use the ArtifactCapturePSJob script. It requires powershell 3 or higher, and otherwise throws errors that I haven't handled yet. Just use the autorunsc script instead for now.




