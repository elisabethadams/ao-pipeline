#!/usr/bin/env python
#
# Step 5 of AO compilation pipeline: make tables
#     Prereqs:
#       0. run step3-findlimits.py (makes OBJECT_Filt.fits_lim.tsv, assumed to exist in this script)
#     This script will:
#       1. make a table of all objects and limits from 0.1"-4"
#       2. make plot of companions vs. distance with limits overlaid

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
import grabBag as gb
import kepler

### Read in which objects to use
if os.path.exists("usingObjects.txt"):
	data = open("usingObjects.txt","r")
	useObjects = []
	lines = data.readlines()
	for line in lines:
		useObjects.append(line.rstrip())
else:
	print "The file does not exist. Running all objects..."
	objectDirListing=os.listdir(ao.objectsDir)
	useObjects = []
	for obj in objectDirListing:
		useObjects.append(obj)

print "Using:",useObjects
filters = ao.filterNames
print "Searching for filters:",filters

## Import settings files
settings={}
fwhmDict={}
for obj in useObjects:
	settings[obj]={}
	settings[obj]=ao.readSettingsFile(ao.settingsFile(obj))
	## Import stars file
	starInfo=ao.readStarsFile(ao.starsFile(obj),delimiter="\t")
	for filt in filters:
		fwhmDict[obj,filt] = "NA"
		for xx in starInfo:
			if xx[0] == filt:
				fwhmDict[obj, filt] = xx[2]

#print fwhmDict

################### END PREAMBLE ############################


#### Import limiting mag files
bigDict={}; byApDict={}
for filt in filters:
	for obj in useObjects:
		arcsec=[];mags=[]
		fitsFile=ao.koiFilterDir(obj,filt)+ao.finalKOIimageFile(obj,filt)
		magFile=fitsFile+"_lim.tsv"
	#	print magFile
		if os.path.isfile(magFile):
			deltaMagDict = ao.importLimitingMagFile(magFile)
			keylist = deltaMagDict.keys()
			sortedKeys=[]
			for key in deltaMagDict["annuli"]:
				#print key, obj, deltaMagDict[key]
				arcsec.append(key)
				mags.append(deltaMagDict[key])
				byApDict[obj,filt,key] = deltaMagDict[key]
			#print mags, arcsec
			bigDict[obj,filt] = mags
		#### As long as we're at it... figure out the seeing for each image
#		if os.path.isfile(fitsFile+".coo"):
#			fwhm = ao.getFWHM(fitsFile, fitsFile+".coo", fwhmType="Moffat")
#			fwhmDict[obj, filt] = round(eval(fwhm[0]) * eval(settings[obj]["Plate_scale_Ks"]), 2)
#		else:
#			fwhmDict[obj,filt] = "NA"

#print byApDict["K00094","Ks","0.1"]

##################################### Output table ################################
## Table showing limits
def makeTable(filt,objectList=[],extra=""):
	if objectList==[]:
		objectList=useList[filt]
	magSummaryFile=ao.mainDir+"tables/limitingMagSummary_"+filt+extra+".tsv"
	magSummaryFileTex= string.replace(magSummaryFile, ".tsv", ".tex")
	print "\nWriting summary of limits to file:",magSummaryFile
	g = open(magSummaryFile,'w')
	gTex = open(magSummaryFileTex,'w')
	specialAps=["0.05","0.1","0.2","0.5","1.0","2.0","4.0"]
	print >>g, "\t".join(["Object", "FWHM", "2MASS-"+filt, "0.05\"","0.1\"","0.2\"","0.5\"","1.0\"","2.0\"","4.0\""])
	print >>gTex,"\t &".join(["Object", "FWHM", "2MASS-"+filt, "0.05\"","0.1\"","0.2\"","0.5\"","1.0\"","2.0\"","4.0\"","\\\\"])
	for obj in objectList:
		print >>g, "\t".join( gb.flattenList([[obj, str(fwhmDict[obj,filt]), str(eval(settings[obj]["2MASS_"+filt])[0]) ]])),
		print >>gTex, "\t &".join( gb.flattenList([[obj, str(fwhmDict[obj,filt]), str(eval(settings[obj]["2MASS_"+filt])[0]) ]])),
		for ap in specialAps:
			print "ap",ap,fwhmDict[obj,filt]
			if eval(ap) >= eval(fwhmDict[obj,filt]):
				print "..."
				print >>g, round(byApDict[obj,filt,ap],2), "\t",
				print >>gTex, round(byApDict[obj,filt,ap],2), "\t &",
			else:
				print >>g, "-- \t",
				print >>gTex, "-- &",
		print >>g, ""
		print >>gTex, "\\\\"
	g.close()


############################ YOU MAY WANT TO KEEP SEVERAL OPTIONS BELOW FOR DIFFERENT SUBSETS ############################

##### Make tables of ALL objects
#makeTable("J")
#makeTable("Ks")

######## For paper AO II -- non Kepler transiting planets in Ks only on ARIES ##########
#### Table I
#nonKeplerObj = ["Corot-1b", "HAT-P-17b", "HAT-P-25b", "HAT-P-30b", "HAT-P-32b", "HAT-P-33b", "HAT-P-6b", "HAT-P-9b", "HD17156b", "TrES-1b", "WASP-1b", "WASP-2b", "WASP-33b", "XO-3b", "XO-4b"]
#makeTable("Ks",objectList=nonKeplerObj,extra="aoII")

makeTable("Ks",objectList=["K00094"],extra="_K00094")
makeTable("J",objectList=["K00094"],extra="_K00094")

