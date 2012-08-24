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
#
allProperNamesKs = ["ABAur", "CQTau", "Corot-1b", "DGTau", "HAT-P-17b", "HAT-P-25b", "HAT-P-30b", "HAT-P-32b", "HAT-P-33b", "HAT-P-6b", "HAT-P-9b", "HD17156b", "IQAur", "K00174", "K00341", "K00555", "K00638", "K00700", "K00961", "K00973", "K00979", "K01054", "K01316", "K01537", "K01883", "RWAur", "RYTau", "TTau", "TrES-1b", "WASP-1b", "WASP-2b", "WASP-33b", "XO-3b", "XO-4b"]
allProperNamesJ = ["RYTau"]
allProperNamesFe = ["CQTau", "DGTau", "RWAur",  "RYTau"]
allProperNamesH2 = ["DGTau", "RWAur", "RYTau", "TTau"]
allProperNamesBr = ["DGTau"]

properName = allProperNamesKs
filt = "Ks"
properName = allProperNamesJ
filt = "J"
properName = allProperNamesFe
filt = "FeII1.64"
properName = allProperNamesBr
filt = "BrG2.16"
properName = allProperNamesH2
filt = "H22.12"



useObjList=[]
for xx in properName:
	useObjList.append("allObj_"+xx+"_"+filt+"_use.txt")

print useObjList


## Now change to that directory
os.chdir(nightPath)


## Copy all files to objects/OBJECT/FILTER/
g = open("summary_"+filt+".txt","w")
for nn,ff in enumerate(useObjList):
	prefix, obj, filt, suffix = ff.split("_")
	objDir = aries.mainObjectPath+obj+"/"
	objFilterDir = objDir+filt[0]+"/"
	if os.path.exists(objDir) == False:
		os.mkdir(objDir)
	if os.path.exists(objFilterDir) == False:
		os.mkdir(objFilterDir)
	if os.path.exists(objFilterDir+"saved/") == False:
		os.mkdir(objFilterDir+"saved/")
	
	## The intermediate steps get saved to a subdirectory
	os.system("cp "+obj+"_"+filt+"* "+objFilterDir+"saved/")
	## The shiftlist, object list, and final image are saved in the main folder
	os.system("cp Shiftlist_"+obj+"_"+filt+".txt "+objFilterDir)
	os.system("cp "+ff+" "+objFilterDir+"allObj_"+obj+"_"+filt+".txt")
	os.system("cp "+obj+"_"+filt+"_mp.fits "+objFilterDir+obj+"_"+filt+".fits")

	## Also we should print the FWHM for our target in the combined image
	finalFrame = obj+"_"+filt+"_mp.fits"
	os.system("rm -f "+finalFrame+".fullcoo")

	ao.findStars(finalFrame, aries.useFWHM, aries.useBkg ,aries.useThresh, extra="")
	worked = aries.readFullCoo(finalFrame, aries.useFWHM, aries.useBkg, aries.useThresh)
	while worked[0] != True:
		useFWHM,useBkg,useThresh = worked
		os.system("rm -f "+finalFrame+".fullcoo")
		ao.findStars(finalFrame,useFWHM,useBkg,useThresh,extra="")
		worked = aries.readFullCoo(finalFrame,useFWHM,useBkg,useThresh)


	measFWHM, measX, measY = ao.getFWHM(finalFrame, finalFrame+".coo", fwhmType=aries.useFWHM)
	print obj,measX, measY, measFWHM, eval(measFWHM)*0.02
	print >>g, obj,measX, measY, measFWHM, eval(measFWHM)*0.02

g.close()
