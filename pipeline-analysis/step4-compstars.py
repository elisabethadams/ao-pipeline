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
	### This should never be set in the settings file!!!
	settings[obj]["Raw_data_dir"] = ao.dataDir + settings[obj]["Night"] + "/"

################### END PREAMBLE ############################

closeDist = 4.1 # arcsec
farDist = 10.0 # arcsec

makeObservingSummary = True

### Figure out which objects have J and or K data
objectDict = {}
for filt in filters:
	objectDict[filt]=[]
	for obj in useObjects:
		if os.path.isfile(ao.koiFilterDir(obj,filt,instrUsed) + ao.finalKOIimageFile(obj,filt,instrUsed)):
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
			fitsFile = ao.koiFilterDir(obj,filt,instrUsed)+ao.finalKOIimageFile(obj,filt,instrUsed)
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
				


####### ####### ####### ####### ####### ####### ####### ####### ####### ####### ####### ####### ####### ####### ####### ####### 
####### Functions to calculate some values: PA ####### 

### The "rotation" is set in koiPlusFilter, and is defined as:
## [number of times to rotate 90 deg, boolean flip up-down, boolean flip left-right], applied in reverse order
def undoRotations(rotation, rawX, rawY):
	theta = rotation[0] * math.pi / 2.
	## derotate first
	derotX = rawX * math.cos(theta) - rawY *math.sin(theta)
	derotY = rawX * math.sin(theta) + rawY *math.cos(theta)
	## then unflip y
	if rotation[1] == True:
		unflipY = derotY * -1
	else:
		unflipY = derotY
	## then unflip x
	if rotation[2] == True:
		unflipX = derotX * -1
	else:
		unflipX = derotX
#	print "Unflipped",unflipX,unflipY
	return unflipX, unflipY	

## Angle from northward arrow to star (via eastward arrow)
# Note: we are defining a triangle with sides A, B, C, and opposite angle alpha, beta, gamma
def getPA(deltaXstar,deltaYstar,northDeltaX,northDeltaY,eastDeltaX,eastDeltaY):
	## the angle from north
	distA = math.sqrt(northDeltaX**2+northDeltaY**2)
	distB = math.sqrt(deltaXstar**2+deltaYstar**2)
	distC = math.sqrt((deltaXstar-northDeltaX)**2+(deltaYstar-northDeltaY)**2)
	angleGammaN = 2 * math.atan( math.sqrt(  (distC**2-(distA-distB)**2) / ((distA+distB)**2-distC**2)  ) )* 180/3.14159
	## the angle from east
	distA = math.sqrt(eastDeltaX**2+eastDeltaY**2)
	distB = math.sqrt(deltaXstar**2+deltaYstar**2)
	distC = math.sqrt((deltaXstar-eastDeltaX)**2+(deltaYstar-eastDeltaY)**2)
	angleGammaE = 2 * math.atan( math.sqrt(  (distC**2-(distA-distB)**2) / ((distA+distB)**2-distC**2)  ) )* 180/3.14159
	## if the east angle is within 90 degrees of east, then use the north angle, otherwise 360-north angle
	if angleGammaE <= 90:
		angleGamma = angleGammaN
	else:
		angleGamma = angleGammaN
	return angleGamma
####### ####### ####### ####### ####### ####### ####### ####### ####### ####### ####### ####### ####### ####### ####### ####### 


##### All stars for one object within a given distLimit in arcsec
def tableForEachStar(obj, distLimit,filt):
#	print "Output all stars within",distLimit,"arcsec to:",ao.starsFile(obj,instrUsed)
	g = open(ao.starsFile(obj,instrUsed),"w")
	print >>g, "\t".join(["object",obj])
	
	if obj in objectDict[filt]:
		
		### Output fwhm for filter
		print >>g, "\t".join([ filt, "fwhm", str(round(fwhmDict[obj,filt],2)) ])
		### Does this object have additional nearby stars on the image?
		apertures, starn, xySkyDict, starDict = ao.readPhotMagFile(ao.koiFilterDir(obj,filt,instrUsed), ao.finalKOIimageFile(obj,filt,instrUsed), magSuffix=".mag")
	#	print os.path.isfile(ao.koiFilterDir(obj,filt,instrUsed)+ao.finalKOIimageFile(obj,filt,instrUsed)+".mag")
		
		### Make a koi class for use in undoing rotations
		k = koiPlusFilter.koiPlusFilter(obj,filt,instrUsed)
		refX = eval(xySkyDict[1][0])
		refY = eval(xySkyDict[1][1])
		refXerr = eval(xySkyDict[1][4])
		refYerr = eval(xySkyDict[1][5])
		if k.dir12 == "N":
			northDeltaX = k.arrowDeltaX12
			northDeltaY = k.arrowDeltaY12
			eastDeltaX = k.arrowDeltaX10
			eastDeltaY = k.arrowDeltaY10
		else:
			northDeltaX = k.arrowDeltaX10
			northDeltaY = k.arrowDeltaY10
			eastDeltaX = k.arrowDeltaX12
			eastDeltaY = k.arrowDeltaY12
		
		
		closeComps = []
		print obj, " has ",len(xySkyDict)-1," comp stars (any distance)"
		### Note stars are 1, not 0, indexed
		for nn in range(1,len(xySkyDict)+1):
			#### Distance ####
		#	distPx = math.sqrt( (eval(xySkyDict[nn][0])-eval(xySkyDict[1][0]))**2 +  (eval(xySkyDict[nn][1])-eval(xySkyDict[1][1]))**2 )
			thisX = eval(xySkyDict[nn][0]) 
			thisY = eval(xySkyDict[nn][1])
			thisXerr = eval(xySkyDict[nn][4])
			thisYerr = eval(xySkyDict[nn][5])
		#	print thisX, thisXerr, thisY, thisYerr, obj, refXerr, refYerr
			deltaX =  thisX - refX
			deltaY =  thisY - refY
			deltaXerr = math.sqrt(thisXerr**2+refXerr**2)
			deltaYerr = math.sqrt(thisYerr**2+refYerr**2)
			## in pixels
			if ((thisX == refX) & (thisY == refY)):
				distPx = math.sqrt( (thisX-refX)**2 + (thisY-refY)**2 )
				distErrPx = 0
			else:
				distPx, distErrPx = gb.distanceWithErrors(deltaX,deltaY,deltaXerr,deltaYerr)
			## in arcsec
			distArcsec = eval(settings[obj]["Plate_scale_"+filt]) * distPx
			distArcsecErr = eval(settings[obj]["Plate_scale_"+filt]) * distErrPx
			## Get position angles in degrees
			useDeltaX, useDeltaY = undoRotations(k.rotation, deltaX, deltaY)
		#	print "\nDiag:",useDeltaX, useDeltaY, "unflipped from",deltaX,deltaY,k.rotation
			if ((thisX == refX) & (thisY == refY)):
				angle = 0
			else:
				angle = getPA(useDeltaX, useDeltaY,northDeltaX,northDeltaY,eastDeltaX,eastDeltaY) 
			#	print "Diag PA:", useDeltaX, useDeltaY, northDeltaX, northDeltaY, eastDeltaX, eastDeltaY, angle
			#### Delta-magnitude ####
			deltaMag = eval(starDict[nn,'5.00'][3])-eval(starDict[1,'5.00'][3])
			### Now check if it is within our desired cutoff distance
			if distArcsec <= distLimit:
				closeComps.append([str(round(distArcsec,2)), str(round(deltaMag,2)), xySkyDict[nn][0], xySkyDict[nn][1], str(round(angle,1))])
		#### We want to output the target star even if there are no others (for its pixel location and fwhm)
	##	print obj,closeComps,"\n\n"
		print >>g, "Star","Dist","Delta-mag","X_pixel","Y_pixel","PA"
		for nn,comp in enumerate(closeComps):
			listOut = gb.flattenList([[str(nn)], closeComps[nn]])
			print >>g, gb.listToString(listOut,tab="\t")
	g.close()

#################################################################################
###              Create star tables for each object                           ###
#################################################################################
for obj in useObjects:	
#	tableForEachStar(obj, closeDist)
	tableForEachStar(obj, farDist, "Ks")
#################################################################################
#################################################################################


## Import dictionary from KSAS
ksasDict = kepler.ksasData(["kepid","posglon","posglat", "kpmag","jmag","kmag"])

######## Make giant summary table for ALL objects
def tableForAllStars(distCutoffArcsec=closeDist, filters =["Ks"], extra=""):
	print "Making table of all stars within:",distCutoffArcsec," arcsec"
	g  = open(ao.compFileSorted(distCutoffArcsec, extra+".tsv"),"w")
	gTex = open(ao.compFileSorted(distCutoffArcsec, extra+".tex"),"w")
	## options for ARIES/Ks only
	delimiter = "\t&"
	print >>gTex, delimiter.join(["KNNNNN", "KeplerID", "KepMag","Kmag", "Star","Dist","PA","$\Delta_{Ks}$", "$Kep_{Dwarf}$", "\\\\"])
	delimiter = "\t"
	print >>g, delimiter.join(["KNNNNN", "KeplerID", "KepMag","Kmag", "Star","Dist","PA","Delta_Ks", "Kep_Dwarf"])
	
	for filt in filters:
		for obj in useObjects:
			firstLineForObj = True # switch this when the first line is output
			## read in the summary file
			ss = open(ao.starsFile(obj,instrUsed),"r")
			lines = ss.readlines()
			ss.close()
			fwhm = lines[1].rstrip().split()[2]
			for line in lines[4:]:
				elems = line.rstrip().split()
				num = elems[0]
				dist = elems[1]
				deltaMag = elems[2]
				xCoord = elems[3]
				yCoord = elems[4]
				pa = elems[5]
				## estimate the kepler mag from K
				try:
					kMag = catalogs.getObjMag2MASS(obj,"Ks")[0]
					jMag = catalogs.getObjMag2MASS(obj,"J")[0]
				except:
					jMag = "--"
					kMag = "--"
			#	print "DIAG:",obj,kMag,jMag
				
				try:
					kepID = ksasDict[obj]["kepid"]
					kepMag = ksasDict[obj]["kpmag"]
					### There used to be a bug here! This should return the Kepler magnitude of the COMPANION, not the TARGET
					if filt == "Ks":
						kepMagDwarf = str(round(kepler.kepMagCiardi("Ks", eval(kMag)+eval(deltaMag)),1))
					elif filt == "J":
						kepMagDwarf = str(round(kepler.kepMagCiardi("J", eval(jMag)+eval(deltaMag)),1))
					else:
						kepMagDwarf = "--"
				except:
					kepID = "--"
					kepMag = "--"
					kepMagDwarf = "--"
				
				### Print info
				if eval(dist) <= distCutoffArcsec:
					if (firstLineForObj):
						output = [obj, kepID, kepMag, kMag, num,dist, pa, deltaMag, kepMagDwarf]
						firstLineForObj = False ## for next star
					else:
						output = ["--", "--", "--","--",  num, dist, pa, deltaMag, kepMagDwarf]
					delimiter = "\t&"
					print >>gTex, delimiter.join(output), "\\\\"
					delimiter = "\t"
					print >>g, delimiter.join(output)
	gTex.close()
	g.close()


#### Run			
#tableForAllStars(distCutoffArcsec=closeDist, extra="")
tableForAllStars(distCutoffArcsec=farDist, extra="_aoIerr")

####### This is to aid step5
print "\nMade star tables for:"
print useObjects
