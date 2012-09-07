#!/usr/bin/env python
#
# Step 0 of AO reduction pipeline: set up night to use
#     This script will:
#       0. create a file that says what night to use (for subsequent scripts)

################## BEGIN PREAMBLE ###########################

import sys
import os
import string

## User packages
pipelineDir = os.path.dirname(os.path.realpath(__file__))
print "This script is stored at:",pipelineDir
moduleDir = string.replace(pipelineDir,"pipeline-reduction","modules")
print "Adding modules from:",moduleDir
sys.path.append(moduleDir) 

#import ao
#################### END PREAMBLE ############################
print "\nSetting up the reduction pipeline..."

#### List everything is the objects directory
aodataDir = "/Users/era/Research/From_Ginshiro/AO/data/"
dataDirListing=os.listdir(aodataDir)


allDates = []
for date in dataDirListing:
#	print date
#	### We assume that all FOLDERS point to real dates
	if os.path.isdir(aodataDir+date):
		allDates.append(date)
print allDates

#### Now pick which to use
print "Data is available for the following dates:",allDates
print "\n Which date should be run?"
for nn in range(len(allDates)):
	print nn," -- ", allDates[nn]
entry = raw_input("Choice (defaults to 0): ")
useDate = allDates[eval(entry)]

print "Using date:",useDate,"\n"

g = open("usingDate.txt","w")
print >>g,useDate
g.close()