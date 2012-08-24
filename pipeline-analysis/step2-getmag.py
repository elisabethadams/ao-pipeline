#!/usr/bin/env python
#
# Step 2 of AO compilation pipeline: find object(s) magnitude(s), distances
#     Prereqs:
#       0. run step1-findstars.py  makes OBJECT_Filt.fits.coo, assumed to exist)
#     This script will:
#       1. create .mag file for all images
#          Note: please use 5.0 pixels as an aperture (default currently); other scripts assume we did

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

################### END PREAMBLE ############################

### Should we overwrite the .mag files if they already exist? Probably not.
overwrite=False


useList={}
for ff in filters:
	useList[ff]=[]
for obj in useObjects:
	for filt in filters:
		imageDir = ao.koiFilterDir(obj,filt)
		image = imageDir + ao.finalKOIimageFile(obj,filt)
		## Make sure the image exists
		if os.path.isfile(image):
			useList[filt].append(obj)
			## Check to see if there are already results from a prior run
			if os.path.isfile(image+".mag"):
				## Delete them if we are redoing things
				if overwrite:
					print "Deleting existing file for",obj
					os.system("rm "+image+".mag")
			## If we're NOT redoing things, we should only proceed if .mag files are missing
			if os.path.isfile(image+".mag"):
				print ".mag file already exists for",obj
			else:
				print "Running",image
				ao.createMagFile(imageDir, image, image+".coo", image+".mag", fullyAutomatic=True, aperturesString='2,5,10', bestSkyAperture='100')	

