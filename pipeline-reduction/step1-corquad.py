#!/usr/bin/env python
#
# Step 1 of ARIES reduction pipeline: making lists
#   This script will:
#    1. create a script to run the corrquad routine
#    2. run corquad.sh
#    3. archive the raw target data

################## BEGIN PREAMBLE ###########################

import os
import sys
import string

## User packages
pipelineDir = os.path.dirname(os.path.realpath(__file__))
print "This script is stored at:",pipelineDir
moduleDir = string.replace(pipelineDir,"pipeline-reduction","modules")
print "Adding modules from:",moduleDir
sys.path.append(moduleDir) 
import ao
import aries
import grabBag as gb

### Read in which objects to use
if os.path.exists("usingDate.txt"):
	data = open("usingDate.txt","r")
	useDates = []
	lines = data.readlines()
	for line in lines:
		useDates.append(line.rstrip())
	# Only use the first one
	useNight = useDates[0]
else:
	sys.exit("I don't know what date to analyze. Please run step0-setup.py")

nightPath = ao.dataDir + useNight + "/"
base = aries.targetBaseName[useNight]
print "Night path:",nightPath, " file name base:", base
################### END PREAMBLE ############################

	

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
scriptName = "corquad.sh"
corquadShell = nightPath+scriptName
g=open(corquadShell, "w")
print >>g, "#!/bin/sh"
print >>g, "corquad="+pipelineDir+"/corquad/corquad"
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
print "Created executable shell script at:",corquadShell

### Run the shell script
os.chdir(nightPath)
os.system("./"+scriptName)

### Make directory for raw data and move it there out of the way
if not os.path.exists("raw/"):
	os.system("mkdir raw")
os.system("mv "+base+"*.fits raw/")
