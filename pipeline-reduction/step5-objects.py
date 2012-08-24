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

import os
import string
from pyraf import iraf

## local packages
import aries
import grabBag as gb


### Pick which night to use
useNight = "20111008"
nightPath = ao.dataDir + useNight + "/"
base = aries.targetBaseName[useNight]
allNights = aries.framesForNights.keys()
nightlyFilterDict={}
for nn in allNights:
	nightlyFilterDict[nn]=[]

### Pick an object (next: read it in from command line)
allObjList = ["allObj_COROT1B_Ks.txt", "allObj_CQTAU_Ks.txt", "allObj_DGTAU_Ks.txt","allObj_HATP6B_Ks.txt", "allObj_HATP17B_Ks.txt", "allObj_HATP25B_Ks.txt",  "allObj_HATP30B_Ks.txt", "allObj_HATP32B_Ks.txt", "allObj_HATP33B_Ks.txt", "allObj_HD17156B_Ks.txt", "allObj_IQAUR_Ks.txt", "allObj_K174_Ks.txt", "allObj_K341_Ks.txt", "allObj_K555_Ks.txt","allObj_K638_Ks.txt", "allObj_K700_Ks.txt", "allObj_K961_Ks.txt", "allObj_K973_Ks.txt", "allObj_K979_Ks.txt", "allObj_K1054_Ks.txt", "allObj_K1316_Ks.txt", "allObj_K1537_Ks.txt", "allObj_TRES-1_Ks.txt", "allObj_WASP1B_Ks.txt",  "allObj_WASP2b_Ks.txt", "allObj_WASP33B_Ks.txt",  "allObj_XO3B_Ks.txt", "allObj_XO-4B_Ks.txt"]

allProperNames = ["Corot-1b","CQTau","DGTau","HAT-P-6b","HAT-P-17b","HAT-P-25b","HAT-P-30b","HAT-P-32b", "HAT-P-33b", "HD17156b", "IQAur", "K00174", "K00341", "K00555","K00638", "K00700", "K00961", "K00973", "K00979", "K01054", "K01316", "K01537", "TrES-1b", "WASP-1b", "WASP-2b", "WASP-33b","XO-3b", "XO-4b"]

allObjList = ["allObj_ABAUR_Ks.txt","allObj_CQTAU_FeII1.64_night2.txt","allObj_DGTAU_BrG2.16.txt", "allObj_DGTAU_FeII1.64_night2.txt", "allObj_DGTAU_H22.12.txt", "allObj_RWAUR_FeII1.64_night2.txt","allObj_RYTAU_FeII1.64_night2.txt", "allObj_RYTAU_H22.12.txt", "allObj_RYTAU_J.txt", "allObj_RYTAU_Ks.txt", "allObj_TTAU_H22.12.txt", "allObj_TTAU_Ks.txt"]
allProperNames =["ABAur","CQTau","DGTau","DGTau", "DGTau", "RWAur", "RYTau", "RYTau", "RYTau", "RYTau", "TTau", "TTau"]

useObjList = ["allObj_K961_Ks.txt", "allObj_K973_Ks.txt", "allObj_K979_Ks.txt"]
properName = [ "K00961", "K00973", "K00979"]
#useObjList = allObjList
#properName = allProperNames
## Varuna needs special handling (too few frames)
#useObjList = ["allObj_VARUNAOCC_Ks.txt"]
#properName = ["VarunaOcc"]


## Now change to that directory
os.chdir(nightPath)

## Copy a fresh bad pixel map 
## Note: we are ignoring bad pixel maps for now
makeNewBPM=False
if makeNewBPM == True:
	if os.path.exists("BPM1.fits"):
		os.system("rm -f BPM1.fits")
	os.system("cp "+ao.pipelineReductionDir+"blankBPM1.fits ./BPM1.fits")


#### Hack: have to do this by hand for now
cr=['\n']

useFWHM = 8.
useBkg = 10.
useThresh = 150.


### .cl file that will contain all objects that need xmosaic
irafScriptFile = "runObjects.cl"
outIRAF = open(irafScriptFile,"w")



## List all files in that directory
allFiles = os.listdir(nightPath)
darkExptimes=[]
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
	allFiles = aries.readFileList(ff)
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
		#### NOTE: This is where we COULD implement lucky imaging
		
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
	# ALSO: don't update the BPM even if you use it! This leads to badness
	irafCommand = "xmos inlist=\"@"+allObjFile+"//.red\" reference=\""+refFrame+"\" output=\""+ext2+"\" expmap=\".exp\" shiftlist=\""+shiftListFile+"\"  fp_xslm=no fp_maskfix=no fp_xzap=no fp_badpixupdate=no fp_mkshifts=no fp_xnregistar=yes mp_mkmask=yes mp_maskdereg=yes mp_xslm=yes mp_maskfix=yes mp_xzap="+useBPM+" mp_badpixupdate=no mp_xnregistar=yes nmean=11 mp_nsigobjms=6. mp_ngrow=1\n\n"
	
	### Dump it in the .cl file
	print >>outIRAF, irafCommand

outIRAF.close()

print "An iraf script called runObjects.cl has been created."
print "It will run xmosaic once for each object and filter, as set in this script."
print "  To invoke from within iraf, in the data directory type:"
print "  (A) xdimsum    [if package is not already loaded]"
print "  (B) cl < runObjects.cl"

