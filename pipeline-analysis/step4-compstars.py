#!/usr/bin/env python
#
# Step 4 of AO compilation pipeline: list all detected comp stars (stars_object.tsv)
#     Prereqs:
#       0. run step2-getmag.py (makes OBJECT_Filt.fits.mag, assumed to exist)
#     This script will:
#       1. list the detected companion stars (assuming everything in .mag file is REAL)

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
for obj in useObjects:
	settings[obj]={}
	settings[obj]=ao.readSettingsFile(ao.settingsFile(obj))

################### END PREAMBLE ############################

closeDist = 10.0 # arcsec

makeObservingSummary = True

### Figure out which objects have J and or K data
objectDict = {}
for filt in filters:
	objectDict[filt]=[]
	for obj in useObjects:
		if os.path.isfile(ao.koiFilterDir(obj,filt) + ao.finalKOIimageFile(obj,filt)):
			objectDict[filt].append(obj)

print "\nThese files have J data:"
print objectDict["J"]
print "\nThese files have Ks data:"
print objectDict["Ks"]

## Get details from .coo file:
initSigma=5.
fwhmDict={}
for filt in filters:
	for obj in objectDict[filt]:
		fwhmDict[obj,filt] =""
		if (obj in useObjects) & (makeObservingSummary == True):
			fitsFile = ao.koiFilterDir(obj,filt)+ao.finalKOIimageFile(obj,filt)
			cooFile = fitsFile+".coo"
			cooFileFull = fitsFile+".fullcoo"
			if os.path.isfile(cooFile):
				data=open(cooFile)
				lines = data.readlines()
				elems=lines[0].rstrip().split(" ")
				initX=eval(elems[0])
				initY=eval(elems[1])
				moffatFWHM= ao.getFWHMfromFITScoo(fitsFile,cooFile)
				fwhm = eval(moffatFWHM)
				fwhmArcsec = fwhm * eval(settings[obj]["Plate_scale_Ks"])
				fwhmDict[obj,filt] = fwhmArcsec
		else:
				print cooFile, " does not exist"
				fwhmDict[obj,filt] = "NA"
				

print fwhmDict


def starTable(obj):
	print "Output to:",ao.starsFile(obj)
	g = open(ao.starsFile(obj),"w")
	print >>g, "\t".join(["object",obj])

	for filt in filters:
		if obj in objectDict[filt]:
			### Output fwhm for filter
			print >>g, "\t".join([ filt, "fwhm", str(round(fwhmDict[obj,filt],2)) ])
			### Does this object have additional nearby stars on the image?
			apertures, starn, xySkyDict, starDict = ao.readPhotMagFile(ao.koiFilterDir(obj,filt), ao.finalKOIimageFile(obj,filt), magSuffix=".mag")
			print os.path.isfile(ao.koiFilterDir(obj,filt)+ao.finalKOIimageFile(obj,filt)+".mag")
			
			closeComps = []
			print obj, " has ",len(xySkyDict)-1," companions at any distance"
			### Note stare are 1, not 0, indexed
			for nn in range(1,len(xySkyDict)+1):
				distPx = math.sqrt( (eval(xySkyDict[nn][0])-eval(xySkyDict[1][0]))**2 +  (eval(xySkyDict[nn][1])-eval(xySkyDict[1][1]))**2 )
				deltaMag = eval(starDict[nn,'5.00'][3])-eval(starDict[1,'5.00'][3])
				distArcsec = eval(settings[obj]["Plate_scale_"+filt]) * distPx
			#	print obj, nn,distArcsec
				if distArcsec <= closeDist:
					closeComps.append([str(round(distArcsec,2)), str(round(deltaMag,2)), xySkyDict[nn][0], xySkyDict[nn][1]])
			#### We want to output the target star even if there are no others (for its pixel location and fwhm)
			print obj,closeComps,"\n\n"
			print >>g, "Star","Dist","Delta-mag","X_pixel","Y_pixel"
			for nn,comp in enumerate(closeComps):
				listOut = gb.flattenList([[str(nn)], closeComps[nn]])
				print >>g, gb.listToString(listOut,tab="\t")


	g.close()

######### Create star tables
for obj in useObjects:	
	starTable(obj)


