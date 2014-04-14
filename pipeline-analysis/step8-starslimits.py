#!/usr/bin/env python
#
# Formerly the script "stars.py" (Created 2011 Aug by era)
#
# Step 8 of AO compilation pipeline: plot stars detected, limits (for some subset)
#     Prereqs:
#       0. run step4-compstars.py (makes OBJECT_stars.tsv, assumed to exist)
#     This script will:
#       1. plot the limits and detected magnitudes for a given filter and set of objects
#
# Notes: useObjects is NOT used; instrument distinctions are not currently made
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

#### Import settings files: NO! 
## It's unnecessary, and some of the limits files are mixed ARIES/PHARO data, 
## which I don't handle as gracefully as I really ought but whatevs
#settings={}
#for obj in useObjects:
#	settings[obj]={}
#	settings[obj]=ao.readSettingsFile(ao.settingsFile(obj,instrUsed))

################### END PREAMBLE ############################

######## Import companion star summary file for set of objects ############

## This file is a HAND COMBINATION of the A and P files for ARIES and PHARO, with duplicate stars removed
starSummaryFile = ao.mainDir+"tables/Stars_within_10.0_aoIerr.tsv"

g = open(starSummaryFile,"r")
lines = g.readlines()
g.close()

headers = lines[0].split("\t")
starDict={};  allStarDeltaKs=[]; allStarDeltaJ=[]; allStarDistsJ=[];allStarPrimariesJ=[]; allStarDistsKs=[];allStarPrimariesKs=[]
for line in lines[1:]:
	elems = line.split("\t")
	### check to see if info is just repeated for same star from previous line
	if elems[0] != "--":
		obj = elems[0]
		objID = elems[1]
		kepMag = elems[2]
		jMag = elems[3]
		kMag = elems[4]
	### all stars have unique values for these fields
	starFilt = elems[5]
	starNum = elems[6]
	starDist = elems[7]
	starPA = elems[8]
	starDeltaMag = elems[9]
	starKepMag = elems[10]
	### Some useful lists and hashes
	starDict[obj,starNum] = [starDist,starDeltaMag,starPA,starKepMag]
	if starFilt == "J":
		allStarPrimariesJ.append(obj)
		allStarDistsJ.append(starDist)
		allStarDeltaJ.append(starDeltaMag)
	elif starFilt == "Ks":
		allStarPrimariesKs.append(obj)
		allStarDistsKs.append(starDist)
		allStarDeltaKs.append(starDeltaMag)
#	if obj == "K00113":
#		print line
#		print obj, starNum, starFilt,  starDeltaMag, starDist

############################ Import Limits ################################

#### Hardcoded for now, because we have so many different limits around ###
extra = "_iqaurARIES"
useFilters = ["Ks"]
###########################################################################

limitDict={}; fwhmDict={}; magDict={}
objList = {}
for filt in useFilters:
	magSummaryFile=ao.mainDir+"tables/limitingMagSummary_"+filt+extra+".tsv"
	g = open(magSummaryFile,"r")
	lines = g.readlines()
	g.close()
	
	headers = lines[0].split("\t")
	apertures1 = headers[4:]
	objList[filt] = []
	limitDict[filt] = {}; fwhmDict[filt] = {}; magDict[filt] = {};
	for line in lines[1:]:
		if line != "\n":
			elems = line.split("\t")
			print elems
			obj = elems[0]
			filterLongName = elems[1]
			fwhm = elems[2]
			mag2mass = elems[3] # J or K depending
			limits = elems[4:]
			limitDict[filt][obj] = limits
			fwhmDict[filt][obj] = fwhm
			magDict[filt][obj] = mag2mass
			objList[filt].append(obj)

	apertures=[]
	for ap in apertures1:
		apertures.append(string.replace(string.replace(ap,"\"",""),"\n",""))
	print apertures

	
################################ Plot subfunctions ############################


def drawLimits(useObjects,filt="Ks",useGrayscale=False):
	colorDict={}
	for ii,obj in enumerate(useObjects):
		if obj not in limitDict[filt].keys():
			print obj + " not found"
		else:
			if useGrayscale:
				colormap = cm.gray((ii)/(float(len(useObjects))),1)
			else:
				colormap = cm.spectral((ii)/(float(len(useObjects))),1)
			dists = []; deltaMag = []
			for xx in range(len(apertures)):
				if limitDict[filt][obj][xx][1] != "-":
					dists.append(eval(apertures[xx]))
					deltaMag.append(eval(limitDict[filt][obj][xx]))
		#	print "\n\n",dists,"\n",deltaMag,"\n\n"
				
			pylab.semilogx(dists,deltaMag,linewidth=2,linestyle='solid',color=colormap,label=obj+" "+instrUsed)
			colorDict[obj]=colormap
	return colorDict
	
	
def makeCompStarPlot(outPlotFile, plotLimitsForObjects=[], hideLegend=False, transparentBkg=False, useFilter="Ks", hack=False,useGrayscale=False):
	pylab.figure(0,figsize=(9,6))
	### Add on limits for select objects
	if plotLimitsForObjects != []:
		colorDict = drawLimits(plotLimitsForObjects,useFilter,useGrayscale)
		highlightedObjects = colorDict.keys()
		print "Highlighting",len(highlightedObjects),"objects:",highlightedObjects
	else:
		colorDict = {}
	#hhhack
	alreadyDrawn=False
	### Check filter
	if useFilter == "J":
		allStarDeltaMag = allStarDeltaJ
		allStarDists = allStarDistsJ
		allStarPrimaries = allStarPrimariesJ
	elif useFilter == "Ks":
		allStarDeltaMag = allStarDeltaKs
		allStarDists = allStarDistsKs
		allStarPrimaries = allStarPrimariesKs

	### Draw companion stars, with a different marker and size for the special ones
	for i in range(len(allStarPrimaries)):
		if allStarPrimaries[i] in highlightedObjects: ## these are special stars that we are highlighting
			pylab.semilogx(eval(allStarDists[i]), eval(allStarDeltaMag[i]), marker="*", linestyle='None',color=colorDict[allStarPrimaries[i]], markeredgewidth=0, markersize=15)
		else: ## regular stars are not highlighted
			pylab.semilogx(eval(allStarDists[i]), eval(allStarDeltaMag[i]), marker="+", linestyle='None',color="k", markersize=10)
	### Settings for plot
	pylab.xlim(xmin=0.08,xmax=11)
	pylab.ylim(ymin=-0.5,ymax=10)
	### make tick marks thicker !!! XX

	### Y increases up (ie, fainter stuff on top) by default
	### For Y to decrease down,toggle this...
	pylab.gca().invert_yaxis()
	if hideLegend == False:	
	### ... and toggle this
		leg = pylab.legend(numpoints=1,loc="lower left")
	#	leg = pylab.legend(numpoints=1,loc="upper left")
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

def makeLimitsPlot(outPlotFile, plotLimitsForObjects=useObjects, hideLegend=False, transparentBkg=False, useFilter="Ks", hack=False,useGrayscale=False):
	pylab.figure(0,figsize=(9,6))
	### Add on limits for select objects
	if plotLimitsForObjects != []:
		colorDict = drawLimits(plotLimitsForObjects,useFilter,useGrayscale)
		highlightedObjects = colorDict.keys()
		print "Highlighting",len(highlightedObjects),"objects:",highlightedObjects
	else:
		colorDict = {}
	#hhhack
	alreadyDrawn=False
	### Settings for plot
	pylab.xlim(xmin=0.08,xmax=11)
	pylab.ylim(ymin=-0.5,ymax=10)
	
	### HACK! IQ Aur's companion star
	pylab.semilogx(7.32, 3.85, marker="*", linestyle='None', markeredgewidth=0, markersize=15)
	

	### Y increases up (ie, fainter stuff on top) by default
	### For Y to decrease down,toggle this...
	pylab.gca().invert_yaxis()
	if hideLegend == False:	
	### ... and toggle this
		leg = pylab.legend(numpoints=1,loc="lower left")
	#	leg = pylab.legend(numpoints=1,loc="upper left")
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
	pylab.savefig(outPlotFile,transparent=transparentBkg)
	pylab.close()


############################## Where things get run ############################
## For paper I erratum on 2009-10 limits (now with 50% fewer IRAF errors)
#erratumPlot = ao.plotDir+"KOI_all_observed_erratum.pdf"
#makeCompStarPlot(erratumPlot, plotLimitsForObjects=['K00085','K00098','K00113'],useGrayscale=True)
#makeCompStarPlot(string.replace(erratumPlot,".pdf",".eps"), plotLimitsForObjects=['K00085','K00098','K00113'],useGrayscale=True)

## IQ Aur
iqaurPlot = ao.plotDir+"IQAur.pdf"
makeLimitsPlot(iqaurPlot, plotLimitsForObjects=['IQAur'], hideLegend=False, useGrayscale=False)
