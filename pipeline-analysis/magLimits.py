#!/usr/bin/env python
#
## Created 2011-04-29 by era
#  Last modified: 2012-07-02 by era
#  This script uses all the final images listed in scripts/pipeline-compile/useObjects.txt (created by step0)
#
#  Prereq: 
#     0. needs .mag file for an image
#  This script will
#       1. find magnitude limit vs distance in filter
#       2. convert from J or Ks to Kep band using Ciardi's equations
#       3. output *fits_lim.tsv file for an image

################## BEGIN PREAMBLE ###########################
import numpy as np
import sys
import os
import math
import string
from pyraf import iraf
import pyfits

# User packages
pipelineDir = os.path.dirname(os.path.realpath(__file__))
moduleDir = string.replace(pipelineDir,"pipeline-analysis","modules/")
#print "Loading modules from",moduleDir,"\n"
sys.path.append(moduleDir) 

import ao
import grabBag as gb
import kepler
import catalogs

################### END PREAMBLE ############################

args = sys.argv
obj = args[1]
filt = args[2]
if len(args)>3:
	instrUsed = str(args[3])
else:
	instrUsed = "ARIES"

### Find the directory and file
fitsDir = ao.koiFilterDir(obj,filt,instrUsed)
fitsFile = ao.finalKOIimageFile(obj,filt)

### Read settings file to get plate scale
settingsDict={}
settingsFile = ao.koiDir(obj,instrUsed)+"settings_"+obj+".tsv"
print settingsFile+"\n"
settingsDict=ao.readSettingsFile(settingsFile)
#### Change if some other Speckle instrument besides Steve Howell's first one (i.e., if Gemini)
if instrUsed == "Speckle":
	try:
		plateScale = eval(settingsDict['Plate_scale_Speckle'])
	except:
		print "\n\nWARNING! using hardcoded plate scale in magLimits.py\n\n"
		plateScale = 0.0228156
#### Should we ever have plate scales differ on different filters, this will need to change
else:
	plateScale = eval(settingsDict['Plate_scale_Ks'])

print "USING PLATE SCALE FOR",instrUsed,":",plateScale


### Read in .mag file 
apertures, numStars, xySkyDict, starDict = ao.readPhotMagFile(fitsDir,fitsFile,magSuffix=".mag")

print "Read .mag file: numStars=",numStars," apertures: ",apertures

#### How significant do we want our contours to be?
nSigma=5

### Set up ranges of arcsec; they have different spacing so we don't waste time on a fine grid away from the star
#### We could set the inner angle based on the seeing, but it's easier to just get rid of the close ones later

### This is set up to mimic the way the code was run back in summer '12
legacyMode = True
if legacyMode == True:
	plateScale = 0.02 ### you'll have a problem if it is actually 0.04
	### How wide are our annuli?
	deltaArcsec=0.1 # arcsec wide disks
	delta = deltaArcsec / plateScale
	#
	aa = np.arange(0.0125 ,0.45, deltaArcsec/4.)
	#print aa
	bb = np.arange(0.45, 2.05, deltaArcsec)
	cc = np.arange(2.5, 10.05, deltaArcsec*10)
	annuliArcsec =aa.tolist() + bb.tolist()+ cc.tolist()
	midAnnuliArcsec = np.array( (aa+deltaArcsec/8.).tolist() + (bb+deltaArcsec/2.).tolist() + (cc+deltaArcsec*5.).tolist())
	annuli = np.array(annuliArcsec) / plateScale

else:
	####### Redo to guarantee the same apertures
	aa = np.array([0.05,0.10,0.15,0.20])
	aa2 = np.array([0.025,0.05,0.10,0.15,0.20])
	#print aa
	bb = np.array([0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
	cc = np.array([2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0])
	
	if instrUsed == "Speckle":
		midAnnuliArcsec =aa2.tolist() + bb.tolist()
		annuliArcsec = np.array( (aa2-0.025).tolist() + (bb-0.05).tolist())
		annuli = np.array(annuliArcsec) / plateScale
	else:
		midAnnuliArcsec =aa.tolist() + bb.tolist()+ cc.tolist()
		annuliArcsec = np.array( (aa-0.025).tolist() + (bb-0.05).tolist() + (cc-0.5).tolist())
		annuli = np.array(annuliArcsec) / plateScale


print "Annuli:", annuli,"\n"


cr=['\n']
def getSkyMeanSDinAnnulus(ann,delta=5):
	iraf.noao()
	iraf.digiphot()
	iraf.apphot()
	iraf.photpars.setParam('apertures','1')
	iraf.phot.setParam('interactive','no')
	iraf.phot.setParam('image',fitsDir+fitsFile)
	iraf.phot.setParam('coords',fitsDir+fitsFile+".coo")
	outmag=".maglim"
	try:	
		os.remove(fitsDir+fitsFile+outmag)
	except:
		print "File does not exist BEFORE running phot, so no need to delete."
	iraf.phot.setParam('output',fitsDir+fitsFile+outmag)
	iraf.phot.setParam('interac','no')	
	iraf.fitskypars.setParam('annulus',str(ann))	
	iraf.fitskypars.setParam('dannulus',str(delta))

	iraf.phot(fitsDir+fitsFile,Stdin=cr)	
	aa, nn, xx, ss = ao.readPhotMagFile(fitsDir,fitsFile,outmag)
	try:	
		os.remove(fitsDir+fitsFile+outmag)
	except:
		print "File not found to delete AFTER running phot; that's odd."
	return xx



skyBkgDict={}
for ann in annuli:
	magDictsForAllStars = getSkyMeanSDinAnnulus(ann,delta=5)
	skyBkgDict[ann]=magDictsForAllStars[1] ######### SHOULDN'T THIS BE 0??? XX XX XX 

##print "Compare the 5 sigma background level at each annulus to the counts in a 10 px aperture"
##refCounts=eval(starDict[1,useAp][2])
##refMag=eval(starDict[1,useAp][3])
#
### Find peak counts on target for comparison (search within a small box around the center)
smallBox=5
def getPeakPixel():
	x1=int(eval(xySkyDict[1][0]))-smallBox
	x2=int(eval(xySkyDict[1][0]))+smallBox
	y1=int(eval(xySkyDict[1][1]))-smallBox
	y2=int(eval(xySkyDict[1][1]))+smallBox
	foo = iraf.imstat(fitsDir+fitsFile+"["+str(x1)+":"+str(x2)+","+str(y1)+":"+str(y2)+"]",Stdout=1)
	# assumes max is last thing in imstat
	bar = foo[-1].split()[-1]
	return eval(bar)

peakPixelCount=getPeakPixel()


############# Get 2MASS magnitude ############
print filt
try:
	if filt == "J":
		ourMag = float(eval(settingsDict["2MASS_J"])[0])		
	elif filt == "H":
		ourMag = float(eval(settingsDict["2MASS_H"])[0])		
	elif filt == "Ks":
		ourMag = float(eval(settingsDict["2MASS_Ks"])[0])		
	else: ### We should get other catalogs in here!
		ourMag = "NA"
except:
	ourMag = "NA"

try:
	kepMag = kepler.kepMagCiardi(filt,ourMag)
except:
	kepMag = "NA"
	

###########################################################################
print "\n\n",annuli,skyBkgDict,"\n\n"


### Create output file
limMagFile=ao.limMagFile(obj,filt,instrUsed)
g = open(limMagFile,'w')
print >>g,"File:",fitsFile
#print >>g,"Camera-mode:",cameraMode
print >>g,"Peak-counts:",peakPixelCount
print >>g,"Sigma:",nSigma
print >>g,"2MASS-"+filt,ourMag
print >>g,"Annulus-mean","Annulus-sd","Annulus-start_px","Annulus-start_arcsec","Annulus-mid_arcsec","Delta-mag","Mag-limit","Est-Kp-mag"
######## NEW (20111102): subtract the OUTERMOST annulus from the mean
######## We assume it's far enough from the star. Otherwise, why stop there?
outerMostMean = eval(skyBkgDict[annuli[-1]][2])
print "Outermost sky background:",outerMostMean
for nn in range(len(annuli)):
	ann = annuli[nn]
	midAnn = midAnnuliArcsec[nn] ## the midpoint, not the starting point, for plots
	bkgMean=eval(skyBkgDict[ann][2]) - outerMostMean
	bkgSD=eval(skyBkgDict[ann][3])
	magDiff = -2.5*math.log((nSigma*bkgSD+bkgMean)/(peakPixelCount),10)
	if ourMag == "NA":
		ourTotalMagLimit = "NA"
		ourTotalMagLimitString = "NA"
		estKepMagLimit = "NA"
	else:
		ourTotalMagLimit = ourMag + magDiff
		ourTotalMagLimitString = str(round(ourTotalMagLimit,2))
		estKepMagLimit = str(round(kepler.kepMagCiardi(filt,ourTotalMagLimit), 2))

	print >>g,"\t".join([str(round(bkgMean,2)), str(round(bkgSD,2)),str(round(ann,2)), str(ann*plateScale), str(midAnn), str(round(magDiff,2)), ourTotalMagLimitString, estKepMagLimit])
g.close()

#print os.system("more "+limMagFile)

print settingsDict
print obj, filt, ourMag, kepMag