#!/usr/bin/env python
#
# Step 4 of ARIES pipeline: Sky subtraction
#   BEFORE running this script, you should:
#    A. ACTUALLY RUN FIRST PASS (using commands generated in step 4) 
#    B  examine the sky-subtracted frames closely
#    C. REMOVE bad frames from the individual object list
# This script will:
#    1. center main object to create Shiftlist for combining frames
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


######################## Pick objects ###################

### List everything with an allObj file in the data directory
objectDirListing=os.listdir(nightPath)

allObjList = []
allProperNames = []
nn=0
print "\nThe following object lists are available:"
for xx in objectDirListing:
	if xx.startswith("allObj") & xx.endswith(".txt"): 	
		allObjList.append(xx)
		elems = xx.split("_")
		name = aries.getProperName(elems[1])
		filt = elems[2]
		allProperNames.append(name)
		print nn, name, filt
		nn = nn + 1
		
### Now pick which to use
print "\n Which objects and filters should be run?"
print "1 -- ALL"
print "2 -- Kepler objects (K*) ONLY, excluding things named NEAR or FIELD"
print "3 -- Non-Kepler objects (not K*) ONLY"
print "4 -- Use subset listed in script (copy and paste into step5-objects.py and rerun)"
entry = raw_input("Choice (defaults to 1): ")

useObjList=[]
if entry == "2":
	for nn,obj in enumerate(allProperNames):
		if ((obj[0]=="K") & (obj.endswith("FIELD")==False) & (obj.endswith("NEAR")==False)):
			useObjList.append(allObjList[nn])
elif entry == "3":
	for nn,obj in enumerate(allProperNames):
		if ((obj[0]!="K") & (obj.endswith("FIELD")==False) & (obj.endswith("NEAR")==False)):
			useObjList.append(allObjList[nn])
elif entry == "4":
	#### Enter your list here
	useObjList = ["allObj_K961_Ks.txt", "allObj_K973_Ks.txt", "allObj_K979_Ks.txt"]

else:
	useObjList = allObjList
	
print "Using object lists:",useObjList,"\n"

g = open("usingObjLists.txt","w")
for obj in useObjList:
	print >>g,obj
g.close()

### Also get the proper names
properName=[]
for ll in allObjList:
	properName.append(aries.getProperNameForAllObjFile(ll))
	
## Now change to the night directory
os.chdir(nightPath)
## List all files in that directory
allFiles = os.listdir(nightPath)

## Copy a fresh bad pixel map 
## Note: we are ignoring bad pixel maps for now
makeNewBPM=False
if makeNewBPM == True:
	if os.path.exists("BPM1.fits"):
		os.system("rm -f BPM1.fits")
	os.system("cp "+ao.pipelineReductionDir+"blankBPM1.fits ./BPM1.fits")


#### You will probably want to adjust these
cr=['\n']

useFWHM = 8.      ## fwhm in pixels of images (5-50+ if the seeing/correction really sucks)
useBkg = 10.      ## variance in background in counts (usually 1-10)
useThresh = 150.  ## sigma above background required to detect a star (10-200 depending)


### .cl file that will contain all objects that need xmosaic
irafScriptFile = "runObjects.cl"
outIRAF = open(irafScriptFile,"w")


### Run through all object list to set them up to be combined into one image with xmosaic's maskpass
for nn,ff in enumerate(useObjList):
	elems=ff.split("_")
	night = elems[0]
	obj = elems[1]
	filt = string.replace(elems[2],".txt","")
	## Some options for xmosaic are set in aries.py for individual objects/filters
	try:
		useFwhm = aries.fwhmTypeForFrame[properName[nn],useNight,filt]
	except:
		useFwhm = aries.fwhmTypeForFrame["default"]
	try:
		useBPM = aries.doBadPixelCorr[properName[nn],useNight,filt]
	except:
		useBPM = aries.doBadPixelCorr["default"]

	print "\n Now working on",ff, "using FWHM type",useFwhm
	allFiles = gb.readListFile(ff)
	## Now get centers, fwhm of brightest object (usually the target)
	shiftListCoords={}
	for frame in allFiles:
		## get rid of existing .coo files
		#os.system("rm -f "+frame+".fullcoo")
		#os.system("rm -f "+frame+".coo")
		### find stars
		if os.path.exists(frame+".fullcoo"):
#			worked = aries.readFullCoo(frame,useFWHM,useBkg,useThresh)
			worked = ao.readFullCooAllStars(frame,useFWHM,useBkg,useThresh)
		else:
			ao.findStars(frame,useFWHM,useBkg,useThresh)
#			worked = aries.readFullCoo(frame,useFWHM,useBkg,useThresh)
			worked = ao.readFullCooAllStars(frame,useFWHM,useBkg,useThresh)
		while worked[0] != True:
			useFWHM,useBkg,useThresh = worked
			os.system("rm -f "+frame+".fullcoo")
			ao.findStars(frame,useFWHM,useBkg,useThresh)
#			worked = aries.readFullCoo(frame,useFWHM,useBkg,useThresh)
			worked = ao.readFullCooAllStars(frame,useFWHM,useBkg,useThresh)
		### Now that we know where the stars are, we can check the FWHM estimate
		measFWHM, measX, measY = ao.getFWHM(frame+"//.red.sub", frame+".coo",fwhmType=useFwhm)
		print frame+" Measured: X, Y (daophot); X, Y, FWHM (imexam)", worked[1] ,worked[2], measX, measY, measFWHM
		if (2 < measFWHM < 50):
			useFWHM = measFWHM		
		#### NOTE: a seeing criteria is used in step6
		
		#shiftListCoords[frame]=[worked[1],worked[2],measFWHM]
		shiftListCoords[frame]=[measX, measY, measFWHM]

	### Now make shiftlist
	shiftListFile="Shiftlist_"+properName[nn]+"_"+filt+".txt"
	allObjFile="allObj_"+properName[nn]+"_"+filt+"_use.txt"
	g = open(shiftListFile,"w")
	gAll = open(allObjFile,"w")
	try:
		refFrame=aries.refFrameForObj[properName[nn],useNight]
	except:
		refFrame = allFiles[1]		
	refX = eval(shiftListCoords[refFrame][0])
	refY = eval(shiftListCoords[refFrame][1])
	for frame in allFiles:
		xx = eval(shiftListCoords[frame][0])
		yy = eval(shiftListCoords[frame][1])
		### The 1.0 needs to be there so the counts don't get rescaled dumbly
		print >>g, frame, xx-refX, yy-refY, "1.0",xx, yy, shiftListCoords[frame][2]
		### At the same time, output the allObj file to be used (predictable name)
		print >>gAll, frame
	g.close()
	gAll.close()

	### Set up commands for iraf .cl script (for the second run, or mask pass, through xmosaic)
	ext2=properName[nn]+"_"+filt
	# mp_nsigobjms=6. mp_ngrow=1 are set high and low resp. to avoid big white blobs
	# defaults were mp_nsigobjms=1.1 and mp_ngrow=3
	# ALSO: never UPDATE the BPM (mp_badpixupdate=no), even if you use it! This leads to badness	
	irafCommand = "xmos inlist=\"@"+allObjFile+"//.red\" reference=\""+refFrame+"\" output=\""+ext2+"\" expmap=\".exp\" shiftlist=\""+shiftListFile+"\"  fp_xslm=no fp_maskfix=no fp_xzap=no fp_badpixupdate=no fp_mkshifts=no fp_xnregistar=yes mp_mkmask=yes mp_maskdereg=yes mp_xslm=yes mp_maskfix=yes mp_xzap="+useBPM+" mp_badpixupdate=no mp_xnregistar=yes nmean=11 mp_nsigobjms=6. mp_ngrow=1\n\n"
	
	### Dump it in the .cl file
	print >>outIRAF, irafCommand

outIRAF.close()

print "An iraf script called runObjects.cl has been created."
print "It will run xmosaic once for each object and filter, as set in this script."
print "  To invoke from within iraf, go to the data directory and type:"
print "  (A) xdimsum    [if package is not already loaded]"
print "  (B) cl < runObjects.cl"

