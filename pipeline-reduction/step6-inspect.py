#!/usr/bin/env python
#
# Step 6 of ARIES pipeline: Weeding out bad FWHM
#   BEFORE running this script, you should:
#    A. run step5 (but NOT xmos if you know you need to ditch frames)
# This script will:
#    1. get rid of objects with bad FWHM
#    2. copy existing Shiftlist, allObj files to .orig
#    3. make a new Shiftlist and allObj files

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
allObjList = ["allObj_CQTAU_Ks.txt", "allObj_DGTAU_Ks.txt","allObj_HATP6B_Ks.txt", "allObj_HATP30B_Ks.txt", "allObj_HATP32B_Ks.txt", "allObj_HD17156B_Ks.txt", "allObj_IQAUR_Ks.txt", "allObj_K174_Ks.txt", "allObj_K341_Ks.txt", "allObj_K555_Ks.txt", "allObj_K700_Ks.txt", "allObj_K961_Ks.txt", "allObj_K973_Ks.txt", "allObj_K979_Ks.txt", "allObj_TRES-1_Ks.txt","allObj_WASP33B_Ks.txt"]

allProperNames = ["CQTau","DGTau","HAT-P-6b","HAT-P-30b","HAT-P-32b","HD17156b", "IQAur", "K00174","K00341","K00555","K00700","K00961","K00973","K00979", "TrES-1b","WASP-33b"]


useObjList = ["allObj_K00961_Ks_use.txt", "allObj_K00973_Ks_use.txt", "allObj_K00979_Ks_use.txt"]
properName = [ "K00961", "K00973", "K00979"]
## Varuna needs special handling (too few frames)
#useObjList = ["allObj_VARUNAOCC_Ks.txt"]
#properName = ["VarunaOcc"]

### How much is too big for the FWHM?
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

## Now change to that directory
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
	print ff, reject, "threshhold means ditching",rejected,"of",len(lines),"frames"
