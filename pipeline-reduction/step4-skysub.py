#!/usr/bin/env python
#
# Step 4 of ARIES pipeline: Sky subtraction
#   BEFORE running this script, you should:
#    A. archive all the calibration files 
#    (skies, masterFlat, normFlat -- everything not qtarget*.red.fits or lists)
#    B. remove all unusably bad frames (saturated, noisy) from the night_filter list  
# This script will:
#    1. use all data from a given filter to run 1st pass through xmosaic sky subtraction
#    2. centroid the brightest object to use for stacking in 2nd pass
#    3. give you statistics so you can reject passed on some FWHM criteria (NOT YET)

import os
import string
from pyraf import iraf

## local packages
import aries
import grabBag as gb


### Pick which night to use
useNight = "20111008"
nightPath = aries.mainDataPath + useNight + "/"
base = aries.targetBaseName[useNight]
allNights = aries.framesForNights.keys()
nightlyFilterDict={}
for nn in allNights:
	nightlyFilterDict[nn]=[]


## Now change to that directory
os.chdir(nightPath)

## Make a new bad pixel map
makeNewBPM=False
if makeNewBPM == True:
	if os.path.exists("BPM1.fits"):
		os.system("rm -f BPM1.fits")
	os.system("cp ../pipeline/blankBPM1.fits ./BPM1.fits")



#### Hack: have to do this by hand for now
#print "Stupid pyraf and xmosaic won't play nice yet, so we'll do this by hand."
#print "Open iraf and change to:",nightPath
#print "Load: xdimsum"

### .cl file that will contain all objects that need xmosaic
print "An iraf script called skysub.cl has been created."
print "It will run xmosaic once for each filter (and night)."
print "  To invoke from within iraf, in the data directory type:"
print "  (A) xdimsum    [if package is not already loaded]"
print "  (B) cl < skysub.cl"
irafScriptFile = "skysub.cl"
outIRAF = open(irafScriptFile,"w")



## List all files in that directory
allFiles = os.listdir(nightPath)
darkExptimes=[]
for ff in allFiles:
	## Find the files for each night
	if ((ff[:5]=="night") & (ff[-1] != "~")):
		print "\n Now working on",ff
		elems=ff.split("_")
		night = elems[0]
		filt = string.replace(elems[1],".txt","")
		allFiles = aries.readFileList(ff)
		## Now sky subtract (1st pass)
		#iraf.xdimsum()
		#print "Running xmosaic 1st pass on", night, filt
		refFrame=allFiles[1]
		#print "Reference frame:",refFrame
		ext1="try1"
		shiftListFile="NA"
		#iraf.xmosaic(inlist="@allObj_K979_Ks.txt", reference=refFrame, output="try1", fp_xslm="yes", fp_maskfix="yes", fp_xzap="yes", fp_badpixupdate="no", fp_xnregistar="no", mp_mkmask="no", mp_maskdereg="no", mp_xslm="no", mp_maskfix="no", mp_xzap="no", mp_badpixupdate="no", mp_xnregistar="no", nmean=9)
#		iraf.xmosaic(inlist="@allObj_K979_Ks.txt//.red", reference="qtarget0575.red.fits",output="try1",shiftlist="NA", expmap = ".exp",nmean=5,Stdin=["\n"])
		#iraf.xmosaic(Stdin=["\n"])
		print >>outIRAF, " xmos inlist=\"@"+ff+"//.red\" reference=\""+refFrame+"\" output=\""+ext1+"\" shiftlist=\"NA\" expmap=\".exp\" nmean=11 \n"
