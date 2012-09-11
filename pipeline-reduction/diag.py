#!/usr/bin/env python
#
# Diagnostic script: why is python unhappy?

################# BEGIN PREAMBLE ###########################

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

#testFile=ao.dataDir+useNight+"/qtarget0449.fits"
#import pyfits
#
#exp= gb.cleanse(ao.getStuffFromHeader(testFile,"EXPTIME",verbose=True))
#
#### M0re tests
#filt = ao.getStuffFromHeader(testFile,"FILTER",verbose=True)
#
#print exp, filt

###### Test Step 5
### List everything with an allObj file in the data directory
#objectDirListing=os.listdir(nightPath)
#
#allObjList = []
#allProperNames = []
#nn=0
#print "\nThe following object lists are available:"
#for xx in objectDirListing:
#	if xx.startswith("allObj") & xx.endswith(".txt"): 	
#		allObjList.append(xx)
#		elems = xx.split("_")
#		name = aries.getProperName(elems[1])
#		allProperNames.append(name)
#		print nn, name
#		nn = nn + 1
#		
#### Now pick which to use
#print "\n Which objects should be run?"
#print "1 -- ALL"
#print "2 -- Kepler objects (K*) ONLY, excluding things named NEAR or FIELD"
#print "3 -- Non-Kepler objects (not K*) ONLY"
#print "4 -- Use subset listed in script (copy and paste into step5-objects.py and rerun)"
#entry = raw_input("Choice (defaults to 1): ")
#
#useObjList=[]
#if entry == "2":
#	for nn,obj in enumerate(allProperNames):
#		if ((obj[0]=="K") & (obj.endswith("FIELD")==False) & (obj.endswith("NEAR")==False)):
#			useObjList.append(allObjList[nn])
#elif entry == "3":
#	for nn,obj in enumerate(allProperNames):
#		if ((obj[0]!="K") & (obj.endswith("FIELD")==False) & (obj.endswith("NEAR")==False)):
#			useObjList.append(allObjList[nn])
#elif entry == "4":
#	#### Enter your list here
#	useObjList = ["allObj_K961_Ks.txt", "allObj_K973_Ks.txt", "allObj_K979_Ks.txt"]
#
#else:
#	useObjList = allObjList
#	
#print "Using object lists:",useObjList,"\n"
#
#g = open("usingObjLists.txt","w")
#for obj in useObjList:
#	print >>g,obj
#g.close()
#

######## Proper names
print aries.getProperName("KOI85")

