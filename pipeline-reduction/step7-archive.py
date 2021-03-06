#!/usr/bin/env python
#
# Step 4 of ARIES pipeline: Sky subtraction
#   BEFORE running this script, you should:
#    A. ACTUALLY RUN FIRST PASS (using commands generated in step 4) 
#    B  examine the sky-subtracted frames closely
#    C. REMOVE bad frames from the individual object list
# This script will:
#    1. center main object to create shiftlist for combining frames
#    2. run final pass through xmosaic to combine individual objects

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


## Now change to the night directory
os.chdir(nightPath)


## Copy all files to objects/OBJECT/FILTER/
g = open("summary_"+useNight+".txt","w")
for nn,ff in enumerate(useObjList):
	elems = ff.split("_")
	prefix = elems[0]
	obj = elems[1]
	filt = elems[2].split(".")[0]  ### gets rid of the trailing .txt
	print "\nCopying files for",obj, filt,"\n"
	objDir = ao.koiDir(obj,instr="ARIES")
	objFilterDir = ao.koiFilterDir(obj,filt,instr="ARIES")
	savedDir = objFilterDir+"saved/"
	print "Making archive directories if they don't already exist"
	if os.path.exists(objDir) == False:
		os.mkdir(objDir)
	if os.path.exists(objFilterDir) == False:
		os.mkdir(objFilterDir)
	if os.path.exists(savedDir) == False:
		os.mkdir(savedDir)
	
	## The shiftlist, object list, and final image are saved in the main folder
	print "Copying shiftfile"
	os.system("cp Shiftlist_"+obj+"_"+filt+".txt "+objFilterDir)
	print "Copying list of frames"
	os.system("cp "+ff+" "+objFilterDir+ff)
	print "Copying final image"
	os.system("cp "+obj+"_"+filt+"_mp.fits "+objFilterDir+obj+"_"+filt+".fits")
	## The intermediate steps get saved to a subdirectory
	print "Copying saved info..."
	os.system("cp "+obj+"_"+filt+"* "+savedDir)

	## Also we should print the FWHM for our target in the combined image
	finalFrame = obj+"_"+filt+"_mp.fits"
	os.system("rm -f "+finalFrame+".fullcoo")

	print "Finding the FWHM for the final frame and exporting to a summary file"
	ao.findStars(finalFrame, aries.useFWHM, aries.useBkg ,aries.useThresh, extra="")
	worked = ao.readFullCooAllStars(finalFrame, aries.useFWHM, aries.useBkg, aries.useThresh, interactive=True)
	while worked[0] != True:
		useFWHM,useBkg,useThresh, useX, useY, useEdge = worked
		os.system("rm -f "+finalFrame+".fullcoo")
		ao.findStars(finalFrame, useFWHM, useBkg, useThresh,extra="")
		worked = ao.readFullCooAllStars(finalFrame, useFWHM, useBkg, useThresh, numXpixels=useX, numYpixels=useY, ignoreEdgePixels=useEdge, interactive=True)


	measFWHM, measX, measY = ao.getFWHM(finalFrame, finalFrame+".coo", fwhmType=aries.useFWHM)
	print obj,measX, measY, measFWHM, eval(measFWHM)*0.02
	print >>g, obj,measX, measY, measFWHM, eval(measFWHM)*0.02

g.close()
