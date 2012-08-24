#!/usr/bin/env python
#
# Step 0 of AO compilation pipeline: find detection limits
#     This script will:
#       0. set which directory has the python modules
#       1. show which objects are available
#       2. allow you to select which to process
#       3. display the final image for each object, filter
#       4. create settings file for each object and filter (including e.g. plate scale)

################## BEGIN PREAMBLE ###########################

import sys
import os
import string
import pylab
import datetime
import math
import matplotlib.cm as cm

# User packages
pipelineDir = os.path.dirname(os.path.realpath(__file__))
moduleDir = string.replace(pipelineDir,"pipeline-analysis","modules")
sys.path.append(moduleDir) 

import ao
import grabBag as gb
import kepler

################### END PREAMBLE ############################

args = sys.argv
rerunLimits = False
if len(args)>1:
	rerunLimits = True

### Set filters to use
filters = ao.filterNames
print "Using filters:",filters,"\n"

### List everything is the objects directory
objectDirListing=os.listdir(ao.objectsDir)

allObjects = []
for obj in objectDirListing:
	print obj
	### We assume that all FOLDERS point to real objects
	if os.path.isdir(ao.objectsDir+obj):
		allObjects.append(obj)

print "All available objects:",allObjects
print "\n Which objects should be run?"
print "1 -- ALL"
print "2 -- Kepler objects (K*) ONLY"
print "3 -- Non-Kepler objects (not K*) ONLY"
print "4 -- Use subset listed in script (copy and paste into step0-setup.py and rerun)"
entry = raw_input("Choice (defaults to 1): ")
useObjects=[]
if entry == "2":
	for obj in allObjects:
		if obj[0]=="K":
			useObjects.append(obj)
elif entry == "3":
	for obj in allObjects:
		if obj[0]!="K":
			useObjects.append(obj)
elif entry == "4":
	#### Enter your list here
	useObjects = ['Corot-1b', 'HAT-P-17b', 'HAT-P-25b', 'HAT-P-30b', 'HAT-P-32b', 'HAT-P-33b', 'HAT-P-6b', 'HAT-P-9b', 'HD17156b', 'TrES-1b',  'WASP-1b', 'WASP-2b', 'WASP-33b', 'XO-3b', 'XO-4b']
#	useObjects = ['Corot-1b']

else:
	useObjects = allObjects
	
print "Using objects:",useObjects,"\n"

g = open("usingObjects.txt","w")
for obj in useObjects:
	print >>g,obj
g.close()


################################## Create settings file ##############################
for obj in useObjects:
	os.system("./createSettings.py "+obj) ## True = we overwrite existing file 



################################## Now display them all ##############################
print "Should we display of the final images in one glorious DS9 window per filter?"
entry = raw_input("y or Y to agree, anything else no: ")
if ((entry == "Y") | (entry == "y")):
	for filt in filters:
		command = "ds9 -zscale -zoom 0.5"
		for obj in useObjects:
			command = command +" " + ao.objectsDir+obj+"/"+filt[0]+"/"+obj + "_"+filt+".fits"
			command = command +" -single &" 
			#print command
		os.system(command) 
