#!/usr/bin/env python
#
# Diagnostic script: why is python unhappy?

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

################### END PREAMBLE ############################



testFile=ao.dataDir+useNight+"/qtarget0449.fits"
import pyfits




exp= gb.cleanse(ao.getStuffFromHeader(testFile,"EXPTIME",verbose=True))


### MOre tests
filt = ao.getStuffFromHeader(testFile,"FILTER",verbose=True)

print exp, filt