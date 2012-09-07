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

## Now change to that directory
os.chdir(nightPath)

## Copy the blank bad pixel map over the copy in the data directory
## We're not really using the bad pixel map these days. 
makeNewBPM=False
if makeNewBPM == True:
	if os.path.exists("BPM1.fits"):
		os.system("rm -f BPM1.fits")
	os.system("cp ../pipeline/blankBPM1.fits ./BPM1.fits")


### Sadly, xmosaic does not work with 

### Create .cl file that will contain all objects that need xmosaic
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
		print >>outIRAF, " xmos inlist=\"@"+ff+"//.red\" reference=\""+refFrame+"\" output=\""+ext1+"\" shiftlist=\"NA\" expmap=\".exp\" nmean=11 \n"
