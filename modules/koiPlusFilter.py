### Very important class definition for AO pipeline plots
# The most important things to check for a new object are:
#   1. Do you want it really zoomed in? 
#		Edit the list in getZoomedBoxSizeForKOI()
#	2. Do you like the default scaling? Run it through once to see what it looks like
#		To tweak the RANGE, go to peakScaleFactorForKOI()
#		To tweak linear vs. log, go to scalingLawForKOI()
#	3. Is the output more-or-less N up and E to the left?
#		Add rotations/flips to 
#	4. Do the arrows look square?
#		They're based on the ref frame and frame +/- 1 around it, so choose a different frame at betterRefNumForKOIfilt()
#	5. Are the arrows positioned right?
#		Adjust offsets at the end of the class definition (c. line 60 in 2012-08-22 version of this script)


import sys
import os 
import pyfits
import numpy as np
import math
## User defined modules, which are in the same directory as koiPlusFilter.py
import ao
import kepler
import grabBag as gb

class koiPlusFilter:
	"""Everything you need to know about a KOI plus filter"""
	def __init__(self,koi,filt,instr="ARIES"):
		self.koi = koi
		self.filt = filt
		self.instr = instr
		self.peakScaleFactor = self.peakScaleFactorForKOI(koi,filt,instr)
		self.rotation = self.rotateImage(koi,filt,instr)
		self.scalingLaw = self.scalingLawForKOI(koi,filt,instr)
		self.betterRefNum = self.betterRefNumForKOIfilt(koi,filt)
		self.zoomedBoxHalfSizeArcsec = self.getZoomedBoxSizeForKOI(koi)
		self.artificialBoostToAvoidZeroBkg=50
		# Directory structure: if data is NOT from ARIES, it still needs to be stored the same way
		self.fitsDir=ao.koiFilterDir(koi,filt,instr)
		self.fitsFile=ao.finalKOIimageFile(koi,filt,instr)
			
		self.cooFile = self.fitsFile+".coo"
		self.shiftListFile=self.fitsDir+ao.shiftListFile(koi,filt)
		## The shiftlist used to be named the same for all objects:
		if os.path.isfile(self.shiftListFile) == False:
			self.shiftListFile = self.fitsDir+"Shiftlist_obj.txt"
		## We can use any extension for the finder plots
		self.outfile = ao.finderPlotName(koi,filt,ext="pdf")
#		print self.koi, self.filt, self.instr
		if self.instr=="ARIES":
			self.setThreeDitherPoints(koi,filt)
			self.doPlotSetup(koi,filt)
		else: #### probably should have something for Lick
			self.doPlotSetupPHARO(koi, filt)
			
		## Want to tweake where the arrows are placed? Nudge things after the setup
		if (koi == "K00013") & (instr == "ARIES"):
			self.extraX = self.extraX +20
			self.extraY = self.extraY - 50
		if (koi == "K00094") & (instr == "ARIES"): 
			self.extraX = self.extraX + 20 ### optimized for big plot
			self.extraY = self.extraY + 780 ### optimized for big plot
		#	self.extraX = self.extraX - 30 ### 12"
		#	self.extraY = self.extraY + 30 ### 12"
		#	self.extraX = self.extraX - 60 ### 24"
		#	self.extraY = self.extraY + 60 ### 24"
		if (koi == "K00097") & (instr == "ARIES"):
			self.extraX = self.extraX -10
			self.extraY = self.extraY - 0
		if (koi == "K00098") & (instr == "ARIES") & (filt == "J"):
			self.extraX = self.extraX -5
			self.extraY = self.extraY +0
		if (koi == "K00098") & (instr == "ARIES") & (filt == "Ks"):
			self.extraX = self.extraX -5
			self.extraY = self.extraY +0
		if (koi == "K00141") & (instr == "ARIES") & (filt == "Ks"):
			self.extraX = self.extraX -5
			self.extraY = self.extraY +0
		if (koi == "K00174") & (instr == "ARIES"):
			self.extraX = self.extraX +2
			self.extraY = self.extraY -10
		if (koi == "K00263") & (instr == "ARIES"):
			self.extraX = self.extraX +60
			self.extraY = self.extraY -10
		if (koi == "K00264") & (instr == "ARIES") & (filt == "J"):
			self.extraX = self.extraX -30
			self.extraY = self.extraY -10
		if (koi == "K00264") & (instr == "ARIES") & (filt == "Ks"):
			self.extraX = self.extraX + 0
			self.extraY = self.extraY - 10
		if (koi == "K00268") & (instr == "ARIES"):
			self.extraX = self.extraX +20
			self.extraY = self.extraY -20
		if (koi == "K00700") & (instr == "ARIES"):
			self.extraX = self.extraX + 0
			self.extraY = self.extraY -150
		if (koi == "K01054") & (instr == "ARIES"):
			self.extraX = self.extraX +150
			self.extraY = self.extraY - 0
		if (koi == "HAT-P-6b") & (instr == "ARIES"):
			self.extraX = self.extraX +0
			self.extraY = self.extraY +20
		if (koi == "HAT-P-9b") & (instr == "ARIES"):
			self.extraX = self.extraX +0
			self.extraY = self.extraY -70
		if (koi == "HAT-P-30b") & (instr == "ARIES"):
			self.extraX = self.extraX +20
			self.extraY = self.extraY -20
		if (koi == "TrES-1b") & (instr == "ARIES"):
			self.extraX = self.extraX +20
			self.extraY = self.extraY -20
		if (koi == "WASP-2b") & (instr == "ARIES"):
			self.extraX = self.extraX -20
			self.extraY = self.extraY -0
		if (koi == "WASP-33b") & (instr == "ARIES"):
			self.extraX = self.extraX +0
			self.extraY = self.extraY - 20
		if (koi == "XO-4b") & (instr == "ARIES"):
			self.extraX = self.extraX +20
			self.extraY = self.extraY -20
		if (koi == "Corot-1b") & (instr == "ARIES"):
			self.extraX = self.extraX +0
			self.extraY = self.extraY -0
		
		
	### Settings for each KOI: what are the ranges in counts for each image
	### It pays to fiddle around with these values, as you can see by the huge range of numbers used
	### The right value depends entirely on where your companion is and how bright the contrast with the primary
	def peakScaleFactorForKOI(self,koi,filt,instr):
		peakScaleFactor={}
		peakScaleFactor[koi,filt,"PHARO"]=[0,20000]
#		peakScaleFactor[koi,filt,"ARIES"]=[0,1000]
		peakScaleFactor[koi,filt,"ARIES"]=[-10,2500] ## for 2011
		peakScaleFactor["K00013","J","ARIES"]=[0.001,3000]
		peakScaleFactor["K00013","Ks","ARIES"]=[-10,3000]
		peakScaleFactor["K00018","J","PHARO"]=[-10,400]
		peakScaleFactor["K00042","J","ARIES"]=[-10,1000]
		peakScaleFactor["K00042","Ks","ARIES"]=[-10,1000]
		peakScaleFactor["K00068","J","ARIES"]=[-20,500]
		peakScaleFactor["K00068","Ks","ARIES"]=[-10,300]
		peakScaleFactor["K00068","J","PHARO"]=[-20,4000]
		peakScaleFactor["K00094","J","ARIES"]=[-40,500]## For Lauren Weiss's paper
		peakScaleFactor["K00094","Ks","ARIES"]=[-40,500] ## For Lauren Weiss's paper
		peakScaleFactor["K00097","J","ARIES"]=[0,1000]
		peakScaleFactor["K00097","Ks","ARIES"]=[0,1000]
		peakScaleFactor["K00098","J","ARIES"]=[10,9000]
		peakScaleFactor["K00098","Ks","ARIES"]=[10,8000]
		peakScaleFactor["K00098","J","PHARO"]=[10,5000]
		peakScaleFactor["K00098","Ks","PHARO"]=[10,5000]
		peakScaleFactor["K00112","J","PHARO"]=[0,11000]
		peakScaleFactor["K00112","Ks","PHARO"]=[0,8000]
		peakScaleFactor["K00113","J","PHARO"]=[-100,12000]
		peakScaleFactor["K00113","Ks","PHARO"]=[-100,5000]
		peakScaleFactor["K00118",filt,"PHARO"]=[-10,5000]
		peakScaleFactor["K00141",filt,"ARIES"]=[-10,2000]
		peakScaleFactor["K00174",filt,"ARIES"]=[0,3000]
		peakScaleFactor["K00264","J","ARIES"]=[0,6000]
		peakScaleFactor["K00264","Ks","ARIES"]=[0,3000]
		peakScaleFactor["K00258",filt,"ARIES"]=[0,800]
		peakScaleFactor["K00268",filt,"ARIES"]=[0,1000]
		peakScaleFactor["K00270","J","ARIES"]=[-100,6000]
		peakScaleFactor["K00270","Ks","ARIES"]=[-100,6000]
		peakScaleFactor["K00284","J","PHARO"]=[-10,10000]
		peakScaleFactor["K00284","Ks","PHARO"]=[-10,10000]
		peakScaleFactor["K00285","J","PHARO"]=[-10,150]
		peakScaleFactor["K00285","Ks","PHARO"]=[0,200]
		peakScaleFactor["K00292","J","PHARO"]=[-10,1500]
		peakScaleFactor["K00292","Ks","PHARO"]=[-10,1500]
		peakScaleFactor["K00555","Ks","ARIES"]=[-20,100]
		peakScaleFactor["K00975","J","ARIES"]=[-10,1500]
		peakScaleFactor["K00975","Ks","ARIES"]=[0,1000]
		peakScaleFactor["K01316","Ks","ARIES"]=[-20,150]
		peakScaleFactor["K01537","Ks","ARIES"]=[-30,11000]
		peakScaleFactor["HAT-P-9b","Ks","ARIES"]=[0,1000]
		peakScaleFactor["HAT-P-30b","Ks","ARIES"]=[-20,100]
		peakScaleFactor["HAT-P-32b","Ks","ARIES"]=[-20,100]
		peakScaleFactor["WASP-2b","Ks","ARIES"]=[-20,800]
		peakScaleFactor["WASP-33b","Ks","ARIES"]=[-20,200]
		peakScaleFactor["TrES-1b","Ks","ARIES"]=[-10,80]
		return peakScaleFactor[koi,filt,instr]
	
	### ARIES does NOT always have E and N in consistent directions
	### Here we define the sequence of flips and rotations to use to get images approximately N up, E left
	def rotateImage(self,koi,filt,instr):
		rotateBy={}
		## [number of times to rotate 90 deg, boolean flip up-down, boolean flip left-right], applied in reverse order
		rotateBy[koi,filt,"PHARO"]=[0, False, False]
		rotateBy[koi,filt,"ARIES"]=[3, True, False]
		rotateBy["K00013",filt,"ARIES"]=[2, False, True]
		rotateBy["K00097",filt,"ARIES"]=[1, True, False]
#		rotateBy["K00094",filt,"ARIES"]=[1, True, False]
		rotateBy["K00098",filt,"ARIES"]=[1, True, False]
		rotateBy["K00141",filt,"ARIES"]=[1, True, False]
		rotateBy["K00264",filt,"ARIES"]=[0, True, False]
		rotateBy["K00268",filt,"ARIES"]=[1, True, False]
		rotateBy["K00270",filt,"ARIES"]=[0, True, False]
		rotateBy["K00975",filt,"ARIES"]=[1, True, False]
		rotateBy["K00258",filt,"ARIES"]=[0, True, False]
		rotateBy["K00174",filt,"ARIES"]=[1, True, False]
		rotateBy["K00341",filt,"ARIES"]=[1, True, True]
		rotateBy["K00555",filt,"ARIES"]=[1, True, False]
		rotateBy["K00638",filt,"ARIES"]=[0, True, False]
		rotateBy["K00700",filt,"ARIES"]=[0, True, False]
		rotateBy["K00961",filt,"ARIES"]=[1, True, False]
		rotateBy["K00973",filt,"ARIES"]=[1, True, False]
		rotateBy["K00979",filt,"ARIES"]=[1, True, False]
		rotateBy["K01054",filt,"ARIES"]=[2, True, False]
		rotateBy["K01316",filt,"ARIES"]=[1, True, False]
		rotateBy["K01537",filt,"ARIES"]=[1, True, False]
		rotateBy["K01883",filt,"ARIES"]=[1, True, False]
		rotateBy["Corot-1b",filt,"ARIES"]=[2, True, False]
		rotateBy["HAT-P-6b",filt,"ARIES"]=[0, True, False]
		rotateBy["HAT-P-17b",filt,"ARIES"]=[1, True, False]
		rotateBy["HAT-P-32b",filt,"ARIES"]=[0, True, False]
		rotateBy["HD17156b",filt,"ARIES"]=[0, True, False]
		rotateBy["TrES-1b",filt,"ARIES"]=[1, True, False]
		rotateBy["WASP-1b",filt,"ARIES"]=[1, True, False]
		rotateBy["WASP-2b",filt,"ARIES"]=[2, True, False]
		rotateBy["WASP-33b",filt,"ARIES"]=[1, True, False]
		rotateBy["XO-3b",filt,"ARIES"]=[0, True, False]
		return rotateBy[koi,filt,instr]
	
	### Do you want the images to display colors on a linear or log scale 
	###  ("zscale" is, alas, not an option, unless you want to write that part)
	def scalingLawForKOI(self,koi,filt,instr):
		if koi in ["K00098","K00113","K00270","K01537"]:
			return "linear"
		else:
			return "log"
	
	## We assume the ref image is a corner of a dither pattern, but it isn't always (set that here)
	def betterRefNumForKOIfilt(self,koi,filt):
		betterRefNum={}
		betterRefNum[koi,filt]=-1
		betterRefNum["K00013","Ks"]=2
		betterRefNum["K00082","J"]=7
		betterRefNum["K00082","Ks"]=10
		betterRefNum["K00261","J"]=26
		betterRefNum["K00268","J"]=3
		betterRefNum["K00270","J"]=10
		betterRefNum["K00555","Ks"]=8
		betterRefNum["K00638","Ks"]=4
		betterRefNum["K00961","Ks"]=3
		betterRefNum["K01316","Ks"]=2
		betterRefNum["K00974","J"]=5
		betterRefNum["K01537","Ks"]=5
		betterRefNum["HAT-P-30b","Ks"]=5
		return betterRefNum[koi,filt]
	

	#### Settings for plot sizes, scales
	## Objects with very close companions should be zooomed in
	def getZoomedBoxSizeForKOI(self,koi):
		# 6 arcsec on a side
		defaultSizeArcsec = 3.0 ### half-size
		# 2 arcsec boxes
		if koi in ["K00098","K00112","K00113","K00174","K00264","K00270","K00292","K01537"]:
			self.lengthScale=0.33  ### i.e., 0.33 * 3 = 1" half-size
			self.labelLengthScale=1.3
			return defaultSizeArcsec*self.lengthScale
		# 8 arcsec boxes
		elif koi in ["K00555","K01316", "HAT-P-30b", "HAT-P-32b", "TrES-1b", "WASP-2b", "WASP-33b"]:
			self.lengthScale=4/3.
			self.labelLengthScale=1.4
			return defaultSizeArcsec*self.lengthScale
		# 12 arcsec boxes
		elif koi in ["K00094"]:
			self.lengthScale=2.
			self.labelLengthScale=1.4
			return defaultSizeArcsec*self.lengthScale
		# 24 arcsec boxes
		elif koi in [""]:
			self.lengthScale=4.
			self.labelLengthScale=1.4
			return defaultSizeArcsec*self.lengthScale
		else:	
			self.lengthScale=1.0
			self.labelLengthScale=1.3
			return defaultSizeArcsec*self.lengthScale
	
	## Figure out E-N arrows from dither pattern
	def setThreeDitherPoints(self, koi, filt):
		# we usually assume the ref frame is point 0, but sometimes not
		shifts = open(self.shiftListFile)
		lines = shifts.readlines()
		shifts.close()
		foundTarget0=False;foundTarget1=False
		lineNum=0
		for line in lines:
			elems = line.split()
			if foundTarget1:
	#			print "got star2"
				self.frame2=elems[0]
				self.nextX2=eval(elems[1])
				self.nextY2=eval(elems[2])
				foundTarget1=False
				foundTarget2=False
			if foundTarget0:
	#			print "got star1"
				self.frame1=elems[0]
				self.nextX1=eval(elems[1])
				self.nextY1=eval(elems[2])
				foundTarget1=True
				foundTarget0=False
			## Either find 0,0, or find the nth frame if chose ref poorly
			if self.betterRefNum == -1:
				if ((eval(elems[1])==0) & (eval(elems[2])==0)):
					foundTarget0=True
			elif lineNum==self.betterRefNum:
				foundTarget0=True
			if foundTarget0 == True:
				self.frame0=elems[0]
#				print "found the ref:",self.frame0
				self.nextX0=eval(elems[1])
				self.nextY0=eval(elems[2])
			lineNum = lineNum+1
#		print "Our three dither points have X coords:", self.nextX0, self.nextX1, self.nextX2, "and Y coords:", self.nextY0, self.nextY1, self.nextY2
	
	def getHeaderOffsets(self,frame):
		hdulist = pyfits.open(frame)
		hdulist.close()	
		offra = hdulist[0].header["OFFRA"]
		offdec = hdulist[0].header["OFFDec"]
		return offra, offdec
	
	
	### Ginormous omnibus function to hand rotatins and flips and rescaling
	def doPlotSetup(self, koi, filt): 
		offra0, offdec0 = self.getHeaderOffsets(ao.getDataDir(koi)+self.frame0)
		offra1, offdec1 = self.getHeaderOffsets(ao.getDataDir(koi)+self.frame1)
		offra2, offdec2 = self.getHeaderOffsets(ao.getDataDir(koi)+self.frame2)
		deltaRA10 = offra1-offra0
		deltaRA12 = offra1-offra2
		deltaDec10 = offdec1-offdec0
		deltaDec12 = offdec1-offdec2
		self.arrowDeltaX12 = self.nextX1-self.nextX2
		self.arrowDeltaY12 = self.nextY1-self.nextY2
		self.arrowDeltaX10 = self.nextX1-self.nextX0
		self.arrowDeltaY10 = self.nextY1-self.nextY0
		if self.rotation[2] == True:
			self.arrowDeltaX12 = -self.arrowDeltaX12
			self.arrowDeltaX10 = -self.arrowDeltaX10
		if self.rotation[1] == True:
		#	print "Flipping up-down "
			self.arrowDeltaY12 = -self.arrowDeltaY12
			self.arrowDeltaY10 = -self.arrowDeltaY10
			
		plateScale= ao.getPlateScaleFromHeader(ao.getDataDir(koi)+self.frame0)
#		print "Star 1-0:  RA delta is ",deltaRA10,", dec delta is ",deltaDec10,", x delta is ",arrowDeltaX10*plateScale,", y delta is ",arrowDeltaY10*plateScale
#		print "Star 1-2:  RA delta is ",deltaRA12,", dec delta is ",deltaDec12,", x delta is ",arrowDeltaX12*plateScale,", y delta is ",arrowDeltaY12*plateScale
		## Now read in coordinates of our target
		coords = open(self.fitsDir+self.cooFile)
		lines = coords.readlines()
		targetCoords = lines[0].split(" ")
		coords.close()
		self.zoomedBoxHalfSize = int(self.zoomedBoxHalfSizeArcsec / plateScale)
#		print plateScale, " arcsec per pixel means boxes are ", zoomedBoxHalfSize
		ctrX=eval(targetCoords[0])
		ctrY=eval(targetCoords[1])
		self.lowerX=round(ctrX)-self.zoomedBoxHalfSize
		self.lowerY=round(ctrY)-self.zoomedBoxHalfSize
		self.upperX=round(ctrX)+self.zoomedBoxHalfSize
		self.upperY=round(ctrY)+self.zoomedBoxHalfSize
		### Read in data
		f = pyfits.open(self.fitsDir+self.fitsFile) 
#		self.scidata = f[0].data
		self.scidata = np.array( f[0].data ) + self.artificialBoostToAvoidZeroBkg
		self.scidataZoomed = self.scidata[self.lowerY:self.upperY,self.lowerX:self.upperX]
		## [number of times to rotate 90 deg, flip x, flip y], done in reverse order
		if self.rotation==[0,False,False]:
			foo = 1
		else:
			if  self.rotation[2] == True:
				self.scidataZoomed = np.fliplr(self.scidataZoomed)
			if  self.rotation[1] == True:
				self.scidataZoomed = np.flipud(self.scidataZoomed)
		self.scidataZoomed = np.rot90(self.scidataZoomed, self.rotation[0])
#		print self.scidataZoomed[1]
		## Number of pixels, peak counts
		self.numY=len(self.scidata)
		self.numX=len(self.scidata[0])
		peakCounts= self.scidata[round(ctrY),round(ctrX)]
		self.scaleMin = self.peakScaleFactor[0]+self.artificialBoostToAvoidZeroBkg#*minVal
		self.scaleMax = self.peakScaleFactor[1]#*maxVal
#		print koi, "scale min, max",self.scaleMin, self.scaleMax
		
		self.numYarcsec = self.numY * plateScale
		self.numXarcsec = self.numX * plateScale
		### Figure out sign ickiness
		## If the change in RA is of larger magnitude between stars 1-0, it is moving E-W 
		if abs(deltaRA10) > abs(deltaRA12):
			self.dir10 ="E"
			self.dir12 ="N"	
			if deltaRA10 > 0: # ie, if the arrow is really W, make it E by flipping
#				print "1-0 axis is W; ", deltaRA10, deltaRA12
				self.arrowDeltaX10 = -self.arrowDeltaX10
				self.arrowDeltaY10 = -self.arrowDeltaY10
#			else:
#				print "1-0 axis is E; ", deltaRA10, deltaRA12
			if deltaDec12 > 0: # ie, if the arrow is really S, make it N by flipping
#				print "1-2 axis is S; ", deltaDec10, deltaDec12
				self.arrowDeltaX12 = -self.arrowDeltaX12
				self.arrowDeltaY12 = -self.arrowDeltaY12
#			else:
#				print "1-2 axis is N; ", deltaDec10, deltaDec12
		## Otherwise 1-2 is the E-W axis
		else:
			self.dir10 ="N"	
			self.dir12 ="E"
			if deltaRA12 > 0:   # ie, if the arrow is really S, make it N by flipping
#				print "1-0 axis is S; ", deltaDec10, deltaDec12
				self.arrowDeltaX12 = -self.arrowDeltaX12
				self.arrowDeltaY12 = -self.arrowDeltaY12
#			else:
#				print "1-0 axis is N; ", deltaDec10, deltaDec12
			if deltaDec10 > 0:  # ie, if the arrow is really W, make it E by flipping
#				print "1-2 axis is W; ", deltaRA10, deltaRA12
				self.arrowDeltaX10 = -self.arrowDeltaX10
				self.arrowDeltaY10 = -self.arrowDeltaY10
#			else:
#				print "1-2 axis is E; ", deltaRA10, deltaRA12
		### Work out rotation here (flips are easier done up above)
		if self.rotation[0] == 1:
			newY10 = self.arrowDeltaX10
			newY12 = self.arrowDeltaX12
			self.arrowDeltaX10 = self.arrowDeltaY10
			self.arrowDeltaY10 = -newY10
			self.arrowDeltaX12 = self.arrowDeltaY12
			self.arrowDeltaY12 = -newY12
		elif self.rotation[0] == 2:
			self.arrowDeltaX10 = -self.arrowDeltaX10
			self.arrowDeltaY10 = -self.arrowDeltaY10
			self.arrowDeltaX12 = -self.arrowDeltaX12
			self.arrowDeltaY12 = -self.arrowDeltaY12
		elif self.rotation[0] == 3:
			newY10 = self.arrowDeltaX10
			newY12 = self.arrowDeltaX12
			self.arrowDeltaX10 = -self.arrowDeltaY10
			self.arrowDeltaY10 = newY10
			self.arrowDeltaX12 = -self.arrowDeltaY12
			self.arrowDeltaY12 = newY12
			
		## Find if x or y is associated with E or N
		if abs(self.arrowDeltaX10) > abs(self.arrowDeltaY10):
			self.xDir ="E"	
			self.arrowOffsetX=cmp(self.arrowDeltaX10,0)*-.7*self.zoomedBoxHalfSize
			self.arrowOffsetY=cmp(self.arrowDeltaY12,0)*-.7*self.zoomedBoxHalfSize
		else:
			self.getExtraOffsetsxDir ="N"
			self.arrowOffsetX=cmp(self.arrowDeltaX12,0)*-.7*self.zoomedBoxHalfSize
			self.arrowOffsetY=cmp(self.arrowDeltaY10,0)*-.7*self.zoomedBoxHalfSize
		
		# Force to be perpendicular! ie, disregard half of the dither pattern so laboriously found above
		self.arrowDeltaX10 = math.copysign(self.arrowDeltaY12,self.arrowDeltaX10)
		self.arrowDeltaY10 = math.copysign(self.arrowDeltaX12,self.arrowDeltaY10)
		#print dir10,arrowDeltaX10,arrowDeltaY10,dir12,arrowDeltaX12,arrowDeltaY12,arrowOffsetX,arrowOffsetY
		## Put center of arrow in correct corner depending on direction of arrows
		extraX12,extraY12=self.findExtraOffsetsSoItLooksPrettier(self.arrowDeltaX12,self.arrowDeltaY12)
		extraX10,extraY10=self.findExtraOffsetsSoItLooksPrettier(self.arrowDeltaX10,self.arrowDeltaY10)
		self.extraX = extraX12 + extraX10
		self.extraY = extraY12 + extraY10
	
	def doPlotSetupPHARO(self, koi, filt): 
		plateScale= 0.0244
		## Now read in coordinates of our target
		coords = open(self.fitsDir+self.cooFile)
		lines = coords.readlines()
		targetCoords = lines[0].split(" ")
#		print "xcvkjdfksdfjsdlkfjlds",targetCoords
		coords.close()
		self.zoomedBoxHalfSize = int(self.zoomedBoxHalfSizeArcsec / plateScale)
#		print plateScale, " arcsec per pixel means boxes are ", self.zoomedBoxHalfSize
		ctrX=eval(targetCoords[0])
		ctrY=eval(targetCoords[1])
		self.lowerX=round(ctrX)-self.zoomedBoxHalfSize
		self.lowerY=round(ctrY)-self.zoomedBoxHalfSize
		self.upperX=round(ctrX)+self.zoomedBoxHalfSize
		self.upperY=round(ctrY)+self.zoomedBoxHalfSize
		### Read in data
		f = pyfits.open(self.fitsDir+self.fitsFile) 
#		self.scidata = f[0].data
		self.scidata = np.array( f[0].data ) + self.artificialBoostToAvoidZeroBkg
		self.scidataZoomed1 = self.scidata[self.lowerY:self.upperY,self.lowerX:self.upperX]
		#	self.scidataZoomed = self.scidataZoomed1.swapaxes(1,0)
		self.scidataZoomed = self.scidataZoomed1
		## Number of pixels, peak counts
		self.numY=len(self.scidata)
		self.numX=len(self.scidata[0])
		peakCounts= self.scidata[round(ctrY),round(ctrX)]
		self.scaleMin = self.peakScaleFactor[0]+self.artificialBoostToAvoidZeroBkg#*peakCounts
		self.scaleMax = self.peakScaleFactor[1]#*peakCounts
#		print koi, "scale min, max",self.scaleMin, self.scaleMax
		self.numYarcsec = self.numY * plateScale
		self.numXarcsec = self.numX * plateScale
		## Assume arrows are all north up and east to the left
		self.arrowOffsetX = 100.*self.lengthScale
		self.arrowOffsetY = -100.*self.lengthScale
		self.arrowDeltaX12 = 0
		self.arrowDeltaY12 = 50
		self.arrowDeltaX10 = -50
		self.arrowDeltaY10 = 0
		self.extraX=0
		self.extraY=0
		self.dir10="E"
		self.dir12="N"
		
	
	# Find offsets so arrows stay on plot
	def findExtraOffsetsSoItLooksPrettier(self,arrowDeltaX,arrowDeltaY):
		labelX1 = self.zoomedBoxHalfSize+self.arrowOffsetX+self.labelLengthScale*self.lengthScale*arrowDeltaX
		labelY1 = self.zoomedBoxHalfSize+self.arrowOffsetY+self.labelLengthScale*self.lengthScale*arrowDeltaY
		extraX =0; extraY=0
		padding = self.zoomedBoxHalfSize*0.1
		if labelX1 < padding:
			extraX = (padding-labelX1)+padding
		if labelX1 > (2*self.zoomedBoxHalfSize-padding):
			extraX = (2*self.zoomedBoxHalfSize-labelX1)-padding
		if labelY1 < padding:
			extraY = (padding-labelY1)+padding
		if labelY1 > (2*self.zoomedBoxHalfSize-padding):
			extraY = (2*self.zoomedBoxHalfSize-labelY1)-padding
		return extraX, extraY
	
