#!/usr/bin/env python
# encoding: utf-8
""" Takes final fits image and makes pdf images """

################## BEGIN PREAMBLE ###########################
import sys
import os
import string
import pylab
import datetime
import math
import matplotlib.cm as cm
from matplotlib.colors import LogNorm

# User packages
pipelineDir = os.path.dirname(os.path.realpath(__file__))
moduleDir = string.replace(pipelineDir,"pipeline-analysis","modules")
sys.path.append(moduleDir) 

import ao
import grabBag as gb
import kepler
import koiPlusFilter
################### END PREAMBLE ############################

def main():
	args = sys.argv
	koi = args[1]
	filt = args[2]
	k = koiPlusFilter.koiPlusFilter(koi,filt)
	makeFinderPlot(k)
#	print ao.getDataDir(koi)

### Settings
## What color scheme
#colorScheme = cm.jet
colorScheme = cm.hot


##### Plotting subfunctions
# Add arrows

def addArrows(k,arrowDeltaX,arrowDeltaY,direction,arrowScale=False):
	desiredSize = 0.5 * k.zoomedBoxHalfSize
	currentSize = math.sqrt(arrowDeltaX**2+arrowDeltaY**2)
	if arrowScale == False:
		arrowScale = desiredSize / currentSize
	
	originX1=k.zoomedBoxHalfSize+k.arrowOffsetX
	originY1=k.zoomedBoxHalfSize+k.arrowOffsetY
	deltaX1 =arrowDeltaX*arrowScale
	deltaY1 =arrowDeltaY*arrowScale
	
	labelX1 = k.zoomedBoxHalfSize+k.arrowOffsetX+arrowDeltaX*arrowScale*k.labelLengthScale - 15*k.lengthScale
	labelY1 = k.zoomedBoxHalfSize+k.arrowOffsetY+arrowDeltaY*arrowScale*k.labelLengthScale - 15*k.lengthScale
	
	print "arrowScale", arrowScale, "origin", originX1+k.extraX, originY1+k.extraY, "delta", deltaX1, deltaY1
		
	pylab.arrow(originX1+k.extraX, originY1+k.extraY, deltaX1, deltaY1, color="white",head_width=8*k.lengthScale,head_length=8*k.lengthScale)
	pylab.text(labelX1+k.extraX,labelY1+k.extraY,direction,color="white")
## Debug;
##	if k.koi in ["K00098","K00270"]:
#	print "XXXXX Labels:", labelX1,labelY1," ARROWS:", originX1,k.extraX, originY1,k.extraY, deltaX1, deltaY1


def fullSizeSubPlot(k,nrows,ncols,plotNum,scaleMin=0,scaleMax=100,showColorBar=True,useColorMap=colorScheme, showArrows=False, useArrowScale=1):
	fullPlot=pylab.subplot(nrows,ncols,plotNum)
	pylab.imshow(k.scidata,cmap=useColorMap,vmin=scaleMin,vmax=scaleMax)
	# Show box
	pylab.plot([k.lowerX,k.lowerX,k.upperX,k.upperX,k.lowerX],[k.lowerY,k.upperY,k.upperY,k.lowerY,k.lowerY],"w--",markersize=10)
	# Show and label scale bar
	scaleOffset=k.zoomedBoxHalfSize/4
	pylab.plot([k.lowerX,k.upperX],[k.upperY+scaleOffset,k.upperY+scaleOffset],"w-",markersize=10)
	pylab.text((k.lowerX+k.upperX)/2,k.upperY+scaleOffset,str(k.zoomedBoxHalfSizeArcsec)+"\"",color="white")
	if showColorBar:
		pylab.colorbar(shrink=0.85)
	if showArrows:
		addArrows(k,k.arrowDeltaX12,k.arrowDeltaY12,k.dir12,arrowScale=useArrowScale)
		addArrows(k,k.arrowDeltaX10,k.arrowDeltaY10,k.dir10,arrowScale=useArrowScale)
	pylab.xlim(xmin=0,xmax=k.numX)
	pylab.ylim(ymin=0,ymax=k.numY)
	fullPlot.set_yticks([])
	fullPlot.set_xticks([])
	pylab.title(k.koi+" "+k.filt+" ("+str(round(k.numXarcsec,1))+"\"x"+str(round(k.numYarcsec,1))+"\")")


def zoomedInSubPlot(k,nrows,ncols,plotNum,scale="log",useColorMap=colorScheme):
#	print "we are subplotting: ",nrows, ncols, plotNum
	zoomedPlot=pylab.subplot(nrows,ncols,plotNum)
	if (k.scalingLaw == "linear") | (scale=="linear"):
		print k.koi, "linear scale"
		zz=pylab.imshow(k.scidataZoomed,cmap=useColorMap,vmin=k.scaleMin,vmax=k.scaleMax)
	else:
		print k.koi, "log scale"
		zz=pylab.imshow(k.scidataZoomed,cmap=useColorMap,vmin=k.scaleMin,vmax=k.scaleMax,norm=LogNorm())
	## Code for colorbar if you want one
	#	pylab.colorbar(zz,cax=zoomedPlot)
	#	pylab.colorbar.make_axes(pylab.gca(), shrink=0.5)
	# Show orientation on smaller plot, along with scale
	addArrows(k,k.arrowDeltaX12, k.arrowDeltaY12,k.dir12)
	addArrows(k,k.arrowDeltaX10, k.arrowDeltaY10,k.dir10)
		
	pylab.xlim(xmin=0,xmax=2*k.zoomedBoxHalfSize)
	pylab.ylim(ymin=0,ymax=2*k.zoomedBoxHalfSize)
	zoomedPlot.set_yticks([])
	zoomedPlot.set_xticks([])
	pylab.title(k.koi+" "+k.filt+" ("+str(round(k.zoomedBoxHalfSizeArcsec,1))+"\"x"+str(round(k.zoomedBoxHalfSizeArcsec,1))+"\")")
	#pylab.title(k.koi+" "+k.filt+" ("+str(round(k.zoomedBoxHalfSizeArcsec,1))+"\")")
	
	return zoomedPlot

# Make plot for individual koi
def makeFinderPlot(k):
	pylab.figure(0,figsize=(10,4))
	### Left plot: full frame to show faint, far stars
	fullSizeSubPlot(k,1,2,1)
	### Right plot: zoomed in around target, rescaled to match peak pixels
	zoomedPlot=zoomedInSubPlot(k,1,2,2)
	pylab.colorbar(shrink=0.85)
	pylab.savefig(k.outfile)
	pylab.close()

# Function to make standalone zoom-plot
def makeZoomedOnlyPlot(k,nrows,ncols,plotNum):
	zoomedPlot = zoomedInSubPlot(nrows,ncols,plotNum)
	return zoomedPlot


### junk
if __name__ == "__main__":
	main()
