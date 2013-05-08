#!/usr/bin/env python
#
# Formerly the script "stars.py" (Created 2011 Aug by era)
#
# Step 8 of AO compilation pipeline: plot stars detected, limits (for some subset)
#     Prereqs:
#       0. run step4-compstars.py (makes OBJECT_stars.tsv, assumed to exist)
#     This script will:
#       1. plot the limits and detected magnitudes for a given filter and set of objects

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
import koiPlusFilter
import catalogs

##### Read in alternate instrument directory (if not "ARIES")
args = sys.argv
if len(args)>1:
	instrUsed = str(args[1])
else:
	instrUsed = "ARIES"
objectDataDir = ao.objDirByInstr(instrUsed)
print "\nLooking for objects in directory: \n "+objectDataDir+"\n"

### Read in which objects to use
if os.path.exists("usingObjects.txt"):
	data = open("usingObjects.txt","r")
	useObjects = []
	lines = data.readlines()
	for line in lines:
		useObjects.append(line.rstrip())
else:
	print "The file does not exist. Running all objects..."
	objectDirListing=os.listdir(objectDataDir)
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
	settings[obj]=ao.readSettingsFile(ao.settingsFile(obj,instrUsed))

################### END PREAMBLE ############################

######## Import companion star summary file for set of objects ############

starSummaryFile = ao.mainDir+"tables/Stars_within_10.0_aoIerr.tsv"

g = open(starSummaryFile,"r")
lines = g.readlines()
g.close()

headers = lines[0].split("\t")
starDict={}; allStarDists=[]; allStarDeltaKs=[]; allStarPrimaries=[]
for line in lines[1:]:
	elems = line.split("\t")
	### check to see if info is just repeated for same star from previous line
	if elems[0] != "--":
		obj = elems[0]
		objID = elems[1]
		kepMag = elems[2]
		kMag = elems[3]
	### all stars have unique values for these fields
	starNum = elems[4]
	starDist = elems[5]
	starPA = elems[6]
	starDeltaKs = elems[7]
	starKepMag = elems[8]
	### Some useful lists and hashes
	starDict[obj,starNum] = [starDist,starDeltaKs,starPA,starKepMag]
	allStarPrimaries.append(obj)
	allStarDists.append(starDist)
	allStarDeltaKs.append(starDeltaKs)


############################ Import Limits ###############################

### Hardcoded for now
filt = "Ks"
extra = "_aoIerratum"
magSummaryFile=ao.mainDir+"tables/limitingMagSummary_"+filt+extra+".tsv"

g = open(magSummaryFile,"r")
lines = g.readlines()
g.close()

headers = lines[0].split("\t")
apertures = headers[3:]
limitDict={}; fwhmDict={}; magDict={}
objList = []
for line in lines[1:]:
	elems = line.split("\t")
	obj = elems[0]
	fwhm = elems[1]
	mag2massK = elems[2]
	limits = elems[3:]
	limitDict[obj] = limits
	fwhmDict[obj] = fwhm
	magDict[obj] = mag2massK
	objList.append(obj)
	
	
################################ Plot subfunctions ############################

def drawLimits(useObjects,filt="Ks"):
	colorDict={}
	for ii,obj in enumerate(useObjects):
		if obj not in limitDict.keys():
			print obj + " not found"
		else:
			colormap = cm.spectral((ii)/(float(len(useObjects))),1)
			#	colormap = cm.gray((ii)/(float(len(useObjects))),1)
			dists = []; deltaMag = []
			for xx in range(len(apertures)):
				if limitDict[obj][xx][1] != "-":
					dists.append(eval(apertures[xx]))
					deltaMag.append(eval(limitDict[obj][xx]))
		#	print "\n\n",dists,"\n",deltaMag,"\n\n"
				
			pylab.semilogx(dists,deltaMag,linewidth=2,linestyle='solid',color=colormap,label=obj+" "+instrUsed)
			colorDict[obj]=colormap
	return colorDict
	
	
def makeCompStarPlot(outPlotFile, plotLimitsForObjects=[], hideLegend=False, transparentBkg=False, useFilter="Ks", hack=False):
	pylab.figure(0,figsize=(9,6))
	### Add on limits for select objects
	if plotLimitsForObjects != []:
		colorDict = drawLimits(plotLimitsForObjects,useFilter)
		highlightedObjects = colorDict.keys()
		print "Highlighting",len(highlightedObjects),"objects:",highlightedObjects
	else:
		colorDict = {}
	#hhhack
	alreadyDrawn=False
	### Draw companion stars, with a different marker and size for the special ones
	for i in range(len(allStarPrimaries)):
		if allStarPrimaries[i] in highlightedObjects: ## these are special stars that we are highlighting
			pylab.semilogx(eval(allStarDists[i]), eval(allStarDeltaKs[i]), marker="*", linestyle='None',color=colorDict[allStarPrimaries[i]], markeredgewidth=0, markersize=15)
		else: ## regular stars are not highlighted
			pylab.semilogx(eval(allStarDists[i]), eval(allStarDeltaKs[i]), marker="+", linestyle='None',color="k", markersize=10)
	### Settings for plot
	pylab.xlim(xmin=0.1,xmax=11)
	pylab.ylim(ymin=-0.5,ymax=10)
	### make tick marks thicker !!! XX

	### Y increases up (ie, fainter stuff on top) by default
	### For Y to decrease down,toggle this...
	#	pylab.gca().invert_yaxis()
	if hideLegend == False:	
	### ... and toggle this
	#	leg = pylab.legend(numpoints=1,loc="lower left")
		leg = pylab.legend(numpoints=1,loc="upper left")
		for t in leg.get_texts():
			t.set_fontsize('small')    # the legend text fontsize
	
	### Now we reformat the plot to make it more legible
	ax = pylab.gca()
	## Bold labels and thick axes
	for tick in ax.xaxis.get_major_ticks():
		tick.label1.set_fontsize(14)
		tick.label1.set_fontweight('bold')
	for tick in ax.yaxis.get_major_ticks():
		tick.label1.set_fontsize(14)
		tick.label1.set_fontweight('bold')
	## Thicker tick marks !! thanks, http://www.krioma.net/blog/2010/05/tickmarks_in_matplotlib.php
	for l in ax.get_xticklines() + ax.get_yticklines(): 
	    l.set_markersize(6) 
	    l.set_markeredgewidth(1.2) 
	for l in ax.yaxis.get_minorticklines()+ax.xaxis.get_minorticklines():
		l.set_markersize(3) 
		l.set_markeredgewidth(1.2)
	## Linear scale on xaxis
	from matplotlib.ticker import ScalarFormatter
#	ax1 = pylab.gca().xaxis
	ax1 = ax.xaxis
	ax1.set_major_formatter(ScalarFormatter())
	## Labels (also in bold)
	pylab.xlabel('Distance from primary (")', fontsize=16, fontweight='bold')
	pylab.ylabel('Magnitude Difference', fontsize=16, fontweight='bold')
#	pylab.xlabel('Distance from primary (")',fontsize=12)
#	pylab.xscale('log')
#	from matplotlib.ticker import ScalarFormatter
	## add completeness dashed line, arrow
	#pylab.axvline(x=5, ymin=0, ymax=1,linestyle="--",color="0.6")
	#pylab.arrow(5,-0.25,-4,0, color="0.6",head_width=.2,head_length=0.1)
	#pylab.text(1.0,0.0,"Spatially complete",color="0.6")
	pylab.savefig(outPlotFile,transparent=transparentBkg)
	pylab.close()



############################## Where things get run ############################
## For paper I erratum on 2009-10 limits (now with 50% fewer IRAF errors)
erratumPlot = ao.plotDir+"KOI_all_observed_erratum.pdf"
makeCompStarPlot(erratumPlot, plotLimitsForObjects=['K00085','K00098','K00113'])