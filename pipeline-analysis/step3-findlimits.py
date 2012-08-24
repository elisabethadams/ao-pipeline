#!/usr/bin/env python
#
# Step 1 of AO compilation pipeline: find detection limits
#     Prereqs:
#       0. run step2-getmag.py (makes OBJECT_Filt.fits.mag, assumed to exist)
#       Also the script "magLimits.py" must exist, because most of the tough stuff lives there
#       Also you will need to make an input catalog of 2MASS mags (see modules/catalogs.py) or else you only get delta-mag
#     This script will:
#       1. find magnitude limit vs distance in filter
#       2. convert from J or Ks to Kep band using Ciardi's equations
#       3. output *fits_lim.tsv file for each image

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
moduleDir = string.replace(pipelineDir,"pipeline-analysis","modules/")
#print "Loading modules from",moduleDir,"\n"
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

############# HACK #############
#useObjects=["HAT-P-30b"]
################################

useList={}
for ff in filters:
	useList[ff]=[]
for obj in useObjects:
	for filt in filters:
		image = ao.koiFilterDir(obj,filt)+ao.finalKOIimageFile(obj,filt)
		print "Does image exist?",image
		if os.path.isfile(image):
			useList[filt].append(obj)
			os.system("./magLimits.py "+obj+" "+filt)
		else:
			print "No such file:", obj, filt

