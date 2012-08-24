#!/usr/bin/env python
#
# Step 1 of AO compilation pipeline: find stars
#     Prereqs:
#       0. run step0-prep.py to get list of objects to work on
#     This script will, for each object and filter:
#       1. find all stars on an image
#       2. determine (interactively) which ones are "good" and output them to a .coo file (target first)

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

### Should we overwrite the .coo files if they already exist? Probably not.
overwrite=False


### Read in summary of target X, Y and FWHM from reduction pipeline
summaryInfo={}
for filt in filters:
	summFile=ao.objectsDir+"summary_"+filt+".txt"
#	print summFile
	if os.path.isfile(summFile):
		data = open(summFile,"r")
		lines = data.readlines()
		for line in lines:
			elems=line.rstrip().split(" ")
			summaryInfo[elems[0],filt] = [elems[1],elems[2],elems[3]] ## x, y, fwhm keyed to object, filter

#print summaryInfo.keys()

#### These are the default values that we use with daophot. You can change them mid-script.
fwhm = 17.
sigma = 1.
thresh = 50.
maxX = 2500
maxY = 2500
edgePixels = 20

### How many objects are in each filter?
useList={}
for ff in filters:
	useList[ff]=[]

### Now make .coo file for all objects, filters
for obj in useObjects:
	for filt in filters:
		image = ao.koiFilterDir(obj,filt)+ao.finalKOIimageFile(obj,filt)
		if os.path.isfile(image):
			useList[filt].append(obj)
			## Find right fwhm, sigma to use
			try:
				targetX, targetY, fwhm = summaryInfo[obj,filt]
			except:
				targetX=0; targetY=0; fwhm=10
			### DON'T run if .coo file already exists and overwrite is set to False
			if ( (os.path.isfile(image+".coo")) & (overwrite == False) ):
				print "\n",obj,"has exisiting .coo file"
				worked = ao.readFullCooAllStars(image, fwhm, sigma, thresh, numXpixels=maxX, numYpixels=maxY, ignoreEdgePixels=edgePixels, interactive=False)
			else:
				print "\n",obj,"will make new .coo file"
				os.system("rm -f "+image+".coo")
				os.system("rm -f "+image+".fullcoo")
				### Now look for the stars in the frame iteratively
				ao.findStars(image, fwhm, sigma, thresh,extra="",overwrite=True)
				### Note! the number of pixels is > 1024 due to combining dithers. In fact, let's just ignore the upper limit
				worked = ao.readFullCooAllStars(image, fwhm, sigma, thresh, numXpixels=maxX, numYpixels=maxY, ignoreEdgePixels=edgePixels)
				# import stars, or loop until conditions improve
				print "first pass?",worked
				while worked[0] != True:
					fwhm, sigma, thresh, maxX, maxY, edgePixels = worked
					print "trying with new values:",fwhm, sigma, thresh
					os.system("rm -f "+image+".fullcoo")
					ao.findStars(image, fwhm, sigma, thresh,overwrite=True)
					worked = ao.readFullCooAllStars(image, fwhm, sigma, thresh, numXpixels=maxX, numYpixels=maxY, ignoreEdgePixels=edgePixels)

			print obj, filt, worked

#for filt in filters:
#	print len(useList[filt]), "objects in", filt, useList[filt]


