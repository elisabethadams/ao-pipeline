#!/usr/bin/env python
#
# #  new 2012-08-10: add 2MASS catalog value for J/H/K
#
#   2014-05-08: get rid of raw data directory, it's too stupid for cross platform work
#  Purpose: to store all of the items needed for a given object in one place
#

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
import aries
import grabBag as gb
import kepler
import catalogs
################### END PREAMBLE ############################

args = sys.argv
### Is this called with one object only? By default do all of them
try:
	obj = args[1]
except:
	obj = "All"
### And is the instrument used other than "ARIES"?
try:
	instrUsed = args[2]
except:
	instrUsed = "ARIES"


useObjects = []
if obj == "All":
	if os.path.exists("usingObjects.txt"):
		data = open("usingObjects.txt","r")
		lines = data.readlines()
		data.close()
		for line in lines:
			obj = line.rstrip()
			useObjects.append(obj)
	else:
		print "usingObjects.txt does not exist. Running all KOIs..."
		koiDirStuff=os.listdir(ao.objectsDir)
		for obj in koiDirStuff:
			if os.path.isdir(ao.objectsDir+obj+"/"):
				useObjects.append(obj)
else:
	useObjects = [obj]	

print "Using objects:",useObjects


### Only set this to True if you want to COMPLETELY ERASE a settings file
rerun = False
#if len(args)>2:
#	if args[2] == "True":
#		rerun = True
#		print "Recreating settings file for "+obj+" from scratch"

## All available settings
## Note that order matters here:
## DEPRECATED: "Raw_data_dir",
allKeys = ["KOI", "Instrument","Night",  "FrameList_J", "FrameList_Ks", "RefFrame_J", "RefFrame_Ks", "Plate_scale_J", "Plate_scale_Ks", "TargetPixelRange_J", "TargetPixelRange_Ks","2MASS_J","2MASS_H","2MASS_Ks"]

### Functions
def setDictValues(keyword):
	# Accept the old value if it exists (though some will be superceded)
#	if oldSettings[keyword] != 'XX':
#		print "This was set to something:",keyword,oldSettings[keyword]
#	else:
#		print "nothing here:",keyword
	if (oldSettings[keyword] != "XX"):
		useValue = oldSettings[keyword]

	# Otherwise set defaults
	elif keyword == "Instrument":
		useValue = instrUsed
	elif keyword == "Night":
		try:
			useValue = aries.objectsForNight[obj] ## a dict, not a function
		except KeyError:
			print "The observing night for",obj,"was not listed in aries.objectsForNight[obj]"
			useValue = "XX"
	elif keyword == "RefFrame_J":
		useValue = "XX"
	elif keyword == "RefFrame_Ks":
		useValue = "XX"
	elif keyword == "Camera_mode":
		useValue = "XX"
	elif keyword == "Plate_scale_J":
		try:
			useValue = ao.getPlateScaleFromHeader(ao.koiFilterDir(obj,"J")+ao.finalKOIimageFile(obj,"J"),True,instrUsed)
		except:
			useValue = "XX"
	elif keyword == "Plate_scale_Ks":
		try:
			useValue = ao.getPlateScaleFromHeader(ao.koiFilterDir(obj,"Ks")+ao.finalKOIimageFile(obj,"Ks"),True,instrUsed)
		except:
			useValue = "XX"
	elif keyword == "2MASS_J":
		useValue = jMag
	elif keyword == "2MASS_H":
		useValue = hMag
	elif keyword == "2MASS_Ks":
		useValue = kMag
	elif keyword == "FrameList_J":
		useValue = obj+"_J"
	elif keyword == "FrameList_Ks":
		useValue =obj+"_Ks"
	elif keyword == "TargetPixelRange_J":
		useValue = [[500,1000],[100,500]]
	elif keyword == "TargetPixelRange_Ks":
		useValue = [[500,1000],[100,500]]
	else:
		useValue = "NA"
	# Here are the ones that get superceded
	if keyword == "KOI":
		useValue = obj
###	if keyword == "Raw_data_dir":
###		useValue = ao.dataDir+settingsDict["Night"]+"/"
		
	# Notify user if there are missing, required entries
	if useValue == "XX":
		print "Need value for: ",obj,keyword
		
	return useValue


##### Read in 2MASS
magDict=catalogs.all2MASS()
objects2MASS = catalogs.get2MASSobjects()
	
for obj in useObjects:
	settingsFile = ao.settingsFile(obj,instrUsed) 
	
	## By default set the oldSettings to not exist (so things work when you add new keywords)
	oldSettings={}

	## Read in existing file if it exists
	if (rerun == False) & (os.path.isfile(settingsFile) == True):
		oldSettings = ao.readSettingsFile(settingsFile)
		print "Reusing prior settings for "+obj
		for key in allKeys:
			if key not in oldSettings.keys():
				oldSettings[key]="XX"
	else:
		for key in allKeys:
			oldSettings[key]="XX"
		print "Recreating settings file from scratch for "+obj

	### Get object 2MASS magnitudes
	if obj in objects2MASS:
		print obj + " is in our 2MASS table with Ks mag:",magDict[obj,"Ks"]
		jMag = catalogs.getObjMag2MASS(obj,"J")
		hMag = catalogs.getObjMag2MASS(obj,"H")
		kMag = catalogs.getObjMag2MASS(obj,"Ks")
	else:
		print obj + " is not in any existing 2MASS catalog. Use catalogs.py to make a list that 2MASS likes; or edit the settings file by hand."
		kMag = "XX"
		jMag = "XX"
		hMag = "XX"

	### Initialize the settings dictionary
	settingsDict={}
	
	### Now set all of the dictionary values to either their defaults or what they were before
	for kk in allKeys:
		settingsDict[kk] = setDictValues(kk)
	
	
	## Print dictionary of settings
	#print "Printing to ",settingsFile
	g = open(settingsFile,'w')
	for kk in allKeys:
		print >>g,kk+"\t",settingsDict[kk]
	g.close()