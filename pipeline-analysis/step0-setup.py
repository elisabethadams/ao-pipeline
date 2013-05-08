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

##### Read in alternate instrument directory (if not "ARIES")
args = sys.argv
if len(args)>1:
	instrUsed = str(args[1])
else:
	instrUsed = "ARIES"
objectDataDir = ao.objDirByInstr(instrUsed)
print "\nLooking for objects in directory: \n "+objectDataDir+"\n"


### Set filters to use
filters = ao.filterNames
print "Using filters:",filters,"\n"

### List everything is the objects directory
objectDirListing=os.listdir(objectDataDir)

allObjects = []
for obj in objectDirListing:
	print obj
	### We assume that all FOLDERS point to real objects
	if os.path.isdir(objectDataDir+obj):
		allObjects.append(obj)


##### Some predetermined lists
objectsNonKepler = ['Corot-1b', 'HAT-P-17b', 'HAT-P-25b', 'HAT-P-30b', 'HAT-P-32b', 'HAT-P-33b', 'HAT-P-6b', 'HAT-P-9b', 'HD17156b', 'TrES-1b',  'WASP-1b', 'WASP-2b', 'WASP-33b', 'XO-3b', 'XO-4b']
objectsARIES2011KOI = [ 'K00174', 'K00341', 'K00555', 'K00638', 'K00700', 'K00961', 'K00973',  'K00979', 'K01054', 'K01316', 'K01537', 'K01883']
objectsPHAROaoI = ["K00005","K00007","K00008","K00010","K00011","K00013","K00017","K00018","K00020","K00022","K00028","K00041","K00064","K00068","K00069","K00070","K00072","K00075","K00084","K00087","K00092","K00098","K00102","K00103","K00104","K00106","K00108","K00109","K00111","K00112","K00113","K00117","K00118","K00121","K00122","K00123","K00124","K00126","K00127","K00137","K00148","K00153","K00180","K00244","K00247","K00249","K00251","K00263","K00265","K00271","K00275","K00281","K00283","K00284","K00285","K00292","K00303","K00306","K00313","K00316","K00364","K00365","K00377"]
testObjects = ['K00977']
################# ENTER LIST HERE #############################
scriptSpecifiedObjects = objectsARIES2011KOI + objectsNonKepler
scriptSpecifiedObjects = objectsPHAROaoI
###############################################################



### Now pick which to use
print "All available objects:",allObjects
print "\n Which objects should be run?"
print "1 -- ALL"
print "2 -- Kepler objects (K*) ONLY"
print "3 -- Non-Kepler objects (not K*) ONLY"
print "4 -- Use subset listed in script (copy and paste into step0-setup.py and rerun)\n",scriptSpecifiedObjects
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
	useObjects = scriptSpecifiedObjects
else:
	useObjects = allObjects
	
print "Using objects:",useObjects,"\n"

g = open("usingObjects.txt","w")
for obj in useObjects:
	print >>g,obj
g.close()


################################## Create settings file ##############################
for obj in useObjects:
	if os.path.isfile(ao.settingsFile(obj,instrUsed)) == False:
		os.system("./createSettings.py "+obj+" "+instrUsed)  
	else:
		print obj, "using existing settings file"

################################## Now display them all ##############################
print "Should we display of the final images in one glorious DS9 window per filter?"
entry = raw_input("y or Y to agree, anything else no: ")
if ((entry == "Y") | (entry == "y")):
	for filt in filters:
		command = "ds9 -zscale -zoom 0.5"
		for obj in useObjects:
			if os.path.isfile(objectDataDir+obj+"/"+filt[0]+"/"+obj + "_"+filt+".fits"):
				command = command +" " + objectDataDir+obj+"/"+filt[0]+"/"+obj + "_"+filt+".fits"
		command = command +" -single &" 
		if command != "ds9 -zscale -zoom 0.5 -single &":
			#print command
			os.system(command) 
