#!/usr/bin/env python
#
# Step 1 of ARIES reduction pipeline: making lists
#   This script will:
#    1. create a script to run the corrquad routine
#    2. run corquad.sh
#    3. archive the raw target data

import os
## local packages
import aries

### Pick which night to use
useNight = "20111008"
nightPath = ao.dataDir + useNight + "/"
base = aries.targetBaseName[useNight]

## all files in that directory
allFiles = os.listdir(nightPath)
targetFiles=[]
for ff in allFiles:
	if len(base) <= len(ff):
		if ff[:len(base)] == base:
			targetFiles.append(ff)
		else:
			foo = "Not a match"
## Make shell script
corquadShell = nightPath+"corquad.sh"
g=open(corquadShell, "w")
print >>g, "#!/bin/sh"
print >>g, "corquad="+aries.reductionPipelinePath+"corquad/corquad"
print >>g, "files=`ls "+base+"*.fits`"
print >>g, "mkdir raw"
print >>g, "for file in $files"
print >>g, "do"
print >>g, "        echo Now correcting ${file}"
print >>g, "        ${corquad} ${file}"
print >>g, "        mv ${file} raw/"
print >>g, "done"
print >>g, "exit 0"
g.close()

os.system("chmod +x "+corquadShell)

### Run the shell script
os.chdir(nightPath)
os.system("chmod +x corquad.sh")

### Make directory for raw data and move it there out of the way
if not os.path.exists("raw/"):
	os.system("mkdir raw")
os.system("mv "+base+"*.fits raw/")
