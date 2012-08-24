#!/usr/bin/env python
#
# Step 5 of AO compilation pipeline: make plots
#     Prereqs:
#       0. run step3-findlimits.py (makes OBJECT_Filt.fits_lim.tsv, assumed to exist in this script)
#     This script will:
#       1. make finder plots for each individual image
#       2. plot a group of objects together (compilation plots for paper, as you specify them here)

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
import finderPlots


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

createIndividualPlots = False

#### Create finder charts for each individual object
if createIndividualPlots:
	for filt in filters:
		for obj in useObjects:
			fitsFile=ao.koiFilterDir(obj,filt)+ao.finalKOIimageFile(obj,filt)
			if os.path.isfile(fitsFile):
				## Could also call finderPlots directly
				os.system("./finderPlots.py "+obj+" "+filt)
			

####### Functions

# Make zoomed-in-only plots for binary KOI
def makeCompositePlotOfZoomedInImages(filt):
	fig=pylab.figure(0,figsize=(12,6))
	nkoi = len(koiForCompositePlot[filt])
	ncols = 6
	if (nkoi % ncols) == 0:
		nrows = nkoi/ncols
	else:
		nrows = nkoi / ncols +1
	print nrows, len(koiForCompositePlot[filt])
	for ii,koi in enumerate(koiForCompositePlot[filt]):
		myKoi = koiPlusFilter.koiPlusFilter(koi,filt)
		print ii, koi, filt
		if os.path.isfile(ao.objectsDir+koi+"/"+filt[0]+"/"+ao.finalKOIimageFile(koi,filt)):
			finderPlots.zoomedInSubPlot(myKoi,nrows,ncols,ii+1)
			pylab.title(koi)
	# Finish and export
	pylab.subplots_adjust(wspace=0.1,hspace=0.1)
	binaryOutfile = ao.plotDir+"allBinaries_"+filt+".pdf"
	pylab.savefig(binaryOutfile)
	pylab.close()

#makeCompositePlotOfZoomedInImages("J")
#makeCompositePlotOfZoomedInImages("Ks")

def makeCompositePlotOfZoomedInImages(koiAndFilterList):
	fig=pylab.figure(0,figsize=(5,10))
	nkoi = len(koiAndFilterList)
	ncols = 1
	if (nkoi % ncols) == 0:
		nrows = nkoi/ncols
	else:
		nrows = nkoi / ncols +1
	print nrows, len(koiAndFilterList)
	
	for ii,kkff in enumerate(koiAndFilterList):
		koi = kkff[0]
		filt = kkff[1]
		myKoi = koiPlusFilter.koiPlusFilter(koi,filt)
		print ii, koi, filt
		if os.path.isfile(ao.objectsDir+koi+"/"+filt[0]+"/"+ao.finalKOIimageFile(koi,filt)):
#			pylab.subplot(nrows,ncols,ii+1)
			finderPlots.zoomedInSubPlot(myKoi,nrows,ncols,ii+1)
					
#			os.system("./finderPlots.py "+koi+" Ks "+str(nrows)+" "+str(ncols)+" "+str(ii+1))
			pylab.title(koi)
	# Finish and export
	pylab.subplots_adjust(wspace=0.1,hspace=0.1)
	binaryOutfile = ao.plotDir+"combined.pdf"
	pylab.savefig(binaryOutfile)
	pylab.close()


#makeCompositePlotOfZoomedInImages([["KOI975","J"],["KOI975","Ks"]])




			
#### Make omnibus combined plot: all filters, J/Ks
def makeOmniPlot(koiList,name,npix,useHalfBox=2.0,ncols=4, scalebarLabel="", noLabels=False, figWidth=12, useFilts=["J","Ks"], useInstr= ["ARIES","PHARO"], plotExt=".pdf"):
	if (npix % ncols) == 0:
		nrows = npix/ncols
	else:
		nrows = npix / ncols +1
	if ncols > 3:
		fig=pylab.figure(0,figsize=(figWidth,3.5*nrows))
	elif ncols ==3:
		fig=pylab.figure(0,figsize=(figWidth,4.25*nrows))
	else:
		fig=pylab.figure(0,figsize=(4,2.5*nrows))
	ii=0
	for koi in koiList:
		if koi == "blank":
			print "leaving blank square"
			ii = ii + 1
		elif koi == "scalebar":
			ax=pylab.subplot(nrows,ncols,ii+1)
			pylab.plot([0,1],[1,1],color="k",linewidth=2.0)
			pylab.text(0.5,1.05, scalebarLabel, color="k", fontsize=18, horizontalalignment='center')
			pylab.xlim(xmin=0,xmax=1)
			pylab.ylim(ymin=0,ymax=1.15)
			pylab.box(on=False)
			ax.set_xticks([])
			ax.set_yticks([])
#			pylab.title(scalebarLabel)
			ii = ii + 1
		else:
			for filt in useFilts:
				for instr in useInstr:
#					print "Looking for object:", ao.koiFilterDir(koi,filt,instr)
					if os.path.isdir(ao.koiFilterDir(koi,filt,instr)):
						print koi, instr, filt, ii
						myKoi = koiPlusFilter.koiPlusFilter(koi,filt,instr)
						finderPlots.zoomedInSubPlot(myKoi,nrows,ncols,ii+1,useColorMap=cm.hot)
						if noLabels == False:
							pylab.title(koi+"\n"+instr+" "+filt)
						ii = ii + 1

	# Finish and export
	pylab.subplots_adjust(wspace=0.1,hspace=0.1)
	binaryOutfile = ao.plotDir+"allBinaries_"+name+plotExt
	if plotExt == ".eps":
		pylab.savefig(binaryOutfile, format='eps')
	else:
		pylab.savefig(binaryOutfile)
	pylab.close()

def makeSingleImagePrettyPlot(koi, outfile, useFilts=["J","Ks"], useInstr="ARIES", showColorBar=True, useScaleMin=0, useScaleMax=100,useColorMap=cm.jet, showArrows=True, useArrowScale=1):
	print "\n gersdaf",useArrowScale,"\nsdlkfjdkfj"
	pylab.figure(0,figsize=(10,5))
	n=0
	for filt in useFilts:
		if os.path.isdir(ao.koiFilterDir(koi,filt,useInstr)):
			n=n+1
	ii=1
	for filt in useFilts:
		if os.path.isdir(ao.koiFilterDir(koi,filt,useInstr)):
	#		print koi, useInstr, filt, ii, useColorMap
			myKoi = koiPlusFilter.koiPlusFilter(koi,filt,useInstr)
			finderPlots.fullSizeSubPlot(myKoi, 1, n, ii, scaleMin=useScaleMin, scaleMax=useScaleMax, showColorBar=showColorBar, useColorMap=useColorMap, showArrows=showArrows,useArrowScale=useArrowScale)
			ii = ii + 1
	if showColorBar:
		pylab.colorbar(shrink=0.85)
	pylab.savefig(outfile)
	pylab.close()	


######################## Some settings for compilation plots I have made ################
#### Note that the scalebars are TEXT labels; the actual size of the scalebar is set in the koiPlusFilter class

### For AJ paper I
#makeOmniPlot(	["K00013","K00018","K00042","blank","scalebar","K00068","blank","K00097","K00118","K00141","K00258","K00268","K00284","K00285","K00975"],"2",28,ncols=4,scalebarLabel="6\"",plotExt=".eps")

#makeOmniPlot(	["K00098","K00112","K00113","K00264","K00270","K00292","blank","scalebar"],"05",16,ncols=4,scalebarLabel="2\"",plotExt=".eps")

### Individual objects
#makeOmniPlot(	["K00258"],"K00258",2,ncols=2,scalebarLabel="xx",plotExt=".eps")
#makeOmniPlot(	["K00268"],"K00268",2,ncols=2,scalebarLabel="xx",plotExt=".eps")

############# Make a single image for a paper (using full image view) ##############
# options:   makeSingleImagePrettyPlot(koi, outfile, useFilts=["J","Ks"], useInstr="ARIES", showColorBar=True, useScaleMin=0, useScaleMax=100,useColorMap=cm.jet, showArrows=True, useArrowScale=1):

#makeSingleImagePrettyPlot("K00094", ao.plotDir+"K00094_paper.eps",showColorBar=False,useScaleMin=30,useScaleMax=80, useColorMap=cm.gray, showArrows=True, useArrowScale=2)
#makeSingleImagePrettyPlot("K00094", ao.plotDir+"K00094_paper.pdf",showColorBar=False,useScaleMin=30,useScaleMax=80, useColorMap=cm.gray, showArrows=True, useArrowScale=2)

############# How to make multiple plots for a paper (using zoomed-in view) ##############
# options:  makeOmniPlot(koiList,name,npix,useHalfBox=2.0,ncols=4, scalebarLabel="", noLabels=False, figWidth=12, useFilts=["J","Ks"], useInstr= ["ARIES","PHARO"], plotExt=".pdf"):

#makeOmniPlot(gb.flattenList([useObjects,["scalebar"]]),"nonkep",16,ncols=4,scalebarLabel="6\"",plotExt=".pdf")
makeOmniPlot(gb.flattenList([useObjects,["scalebar"]]),"nonkep",16,ncols=4,scalebarLabel="6\"",plotExt=".eps")
