#!/usr/bin/env python
#
# Step 6 of ARIES pipeline: Weeding out bad FWHM
#   BEFORE running this script, you should:
#    A. run step5 (but NOT xmos if you know you need to ditch frames)
# This script will:
#    1. get rid of objects with bad FWHM
#    2. copy existing Shiftlist, allObj files to .orig
#    3. make a new Shiftlist and allObj files

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

allNights = aries.framesForNights.keys()
nightlyFilterDict={}
for nn in allNights:
	nightlyFilterDict[nn]=[]


##### Read in the object(s) used in step5
if os.path.exists("usingObjLists.txt"):
	data = open("usingObjLists.txt","r")
	useObjList = []
	properName = []
	lines = data.readlines()
	for line in lines:
		objList = line.rstrip()
		useObjList.append(objList)
		properName.append(aries.getProperNameForAllObjFile(objList))
	print "Using object lists:",useObjList
else:
	sys.exit("I don't know what objects to analyze. Please run step5-objects.py")


######################## Individual settings for objects for this script ########################
### How much is too big for the FWHM (in pixels)?
rejectFWHMover={}
rejectFWHMover["WASP-1b","Ks"] = 15.
rejectFWHMover["WASP-2b","Ks"] = 25. ## TERRIBLE image quality, both stars elongated
rejectFWHMover["K00174","Ks"] = 30. ## Binary, but seeing is never good
rejectFWHMover["K00341","Ks"] = 20. 
rejectFWHMover["K00555","Ks"] = 25.
rejectFWHMover["K00638","Ks"] = 10. ## Lots of frames, mostly 7-9 fwhm
rejectFWHMover["K00700","Ks"] = 40. ## Crummy but very few frames
rejectFWHMover["K01054","Ks"] = 15.
rejectFWHMover["K01316","Ks"] = 10.
rejectFWHMover["K01537"] = 20. ## DOUBLE STAR! This means the FWHM is BIGGER on good frames
rejectFWHMover["HAT-P-17b","Ks"] = 15.
rejectFWHMover["HAT-P-25b","Ks"] = 25. ## crummy!
rejectFWHMover["HAT-P-33b","Ks"] = 8. ## beautiful!
rejectFWHMover["HAT-P-9b","Ks"] = 10. ## starts off well, some worse frames
rejectFWHMover["XO-3b","Ks"] = 6. ## gorgeous!
rejectFWHMover["XO-4b","Ks"] = 7. ## gorgeous!
rejectFWHMover["CQTau","Ks"] = 5. ## wow
rejectFWHMover["DGTau","Ks"] = 20. 
rejectFWHMover["RWAur","H22.12"] = 6. 
rejectFWHMover["RWAur","Ks"] = 10. 
rejectFWHMover["RWAur","FeII1.64"] = 10. 
rejectFWHMover["TrES-1b","Ks"] = 10. 
rejectFWHMover["TTau","H22.12"] = 7. 
rejectFWHMover["TTau","Ks"] = 6. 

## Now change to the night directory
os.chdir(nightPath)

## Read in Shiftlist
for nn,ff in enumerate(useObjList):
	rejected=0
	filt = string.replace(ff.split("_")[2],".txt","")
	try:
		reject = rejectFWHMover[properName[nn],filt]
	except KeyError:
		reject = 50.


	shiftListFileFull="Shiftlist_"+properName[nn]+"_"+filt+"_full.txt"
	shiftListFile="Shiftlist_"+properName[nn]+"_"+filt+".txt"
	allObjFile="allObj_"+properName[nn]+"_"+filt+"_use.txt"
	#if os.path.exists(shiftListFileFull)==True:
	#	print "Full file already exists! Not going to risk an overwrite; go delete it if it offends you."
	#else:	
	os.system("cp "+shiftListFile+" "+shiftListFileFull)

	data = open(shiftListFileFull,"r")
	g = open(shiftListFile,"w")
	gAll = open(allObjFile,"w")
	lines = data.readlines()
	for line in lines:
		elems = line.rstrip().split()
		if len(elems) > 1:
			if elems[-1] != "INDEF":
				fwhm = eval(elems[-1])
				if fwhm < reject:
					print >>g, line.rstrip()
					print >>gAll, elems[0]
				else:
					rejected = rejected + 1
	data.close()
	g.close()
	gAll.close()
	print ff, reject, "px FWHM threshhold means ditching",rejected,"of",len(lines),"frames"
