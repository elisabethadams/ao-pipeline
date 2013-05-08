#!/usr/bin/env python
#
# Created 2011-08-15 by era
#  Contains specialized functions for interacting with Kepler data
#		Ciardi's J-Ks to Kp magnitude
#		Interfaces with KSAS, KFOP output files

import numpy as np
import sys
import os
import math
import string
import pylab

# User packages (also in this same directory)
import ao
import grabBag as gb

#### Kepler-specific inputs
### These need to be periodically updated as new KOIs are added
kfopIDtargetFile = ao.infoDir + "Catalogs/KFOP/targets_all_20120730.html"
defaultKSASfile = ao.infoDir + "Catalogs/KSAS/ksasAllKOI_2011Aug.csv"


### Magnitude conversions: go from J, K, or J-K to estimated Kepler mag
### We really do need ALL of these decimal places
def magKpFromJminusK(J,Ks,startype="Dwarf"):
	x = J - Ks
	if startype == "Dwarf":
		return Ks + 0.314377 + 3.85667*x +3.176111*x**2 - 25.3126*x**3 + 40.7221*x**4 - 19.2112*x**5
	else:
		return Ks + 0.42443603 + 3.7937617*x -2.3267277*x**2 + 1.4602553*x**3

def magKpMinusKsCiardi(Ks):
	if Ks < 15.4:
		return Ks-643.05168 + 246.00603*Ks-37.136501*Ks**2+2.7802622*Ks**3 - 0.10349091*Ks**4 + 0.0015364343*Ks**5
	else:
		return Ks-2.7284+0.3311*Ks

def magKpMinusJCiardi(J):
	if J < 16.7:
		return J-398.04666 + 149.08127*J-21.952130*J**2+1.5968619*J**3 - 0.057478947*J**4 + 0.00082033223*J**5
	else:
		return J+0.1918+0.08156*J

def kepMagCiardi(filt, mag):
	if filt == "J":
		return magKpMinusJCiardi(mag)
	elif filt == "Ks":
		return magKpMinusKsCiardi(mag)
	else:
		return "NA"

def testCiardi():
	### Ciardi test values for K00098
	ciardi={}
	ciardi[12.12,"Ks"]=14.08
	ciardi[13.77,"Ks"]= 15.67
	ciardi[15.38,"Ks"]= 17.75
	ciardi[15.50,"Ks"]= 17.90
	ciardi[15.69,"Ks"]= 18.16
	ciardi[16.16,"Ks"]= 18.78
	ciardi[16.61,"Ks"]= 19.38
	ciardi[16.86,"Ks"]= 19.72
	ciardi[12.08,"J"]=13.51
	ciardi[13.69,"J"]= 15.02
	ciardi[14.31,"J"]= 15.68
	ciardi[15.04,"J"]= 16.46
	ciardi[15.87,"J"]=   17.36
	ciardi[16.50,"J"]=  18.04
	ciardi[17.21,"J"]=  18.81
	ciardi[17.76,"J"]= 19.40
	ciardi[18.17,"J"]=19.84
	#### Test
	print "J    ", "     ","Kp  ", "     ","Compare to Ciardi table"
	for mag in [12.08,13.69,14.31,15.04,15.87,16.50,17.21,17.76,18.17]:
		print round(mag,2), "     ", round(magKpMinusJCiardi(mag),2),"     ", ciardi[mag,"J"]
	print "Ks   ","     ", "Kp  ", "     ","Compare to Ciardi table"
	for mag in [12.12,13.77,15.38,15.50,15.69,16.16,16.61,16.86]:
		print round(mag,2), "     ",round(magKpMinusKsCiardi(mag),2), "     ",ciardi[mag,"Ks"]
		
	return 0	


### Accessing KSAS info
# Possible values for fields list (after removing def2 prefix):
# kepoi_name, kepoi, kepid, teff, teffunc, logg, loggunc, feh, fehunc, posglon, posglonunc, posglat, posglatunc, plx, plxunc, pmtot, pmtotunc, kpmag, kpmagunc, jmag, jmagunc, hmag, hmagunc, kmag, kmagunc, active, tperiod, tperiodunc, transdepth, transdepthunc, transdur, transdurunc, incl, inclunc, sma, smaunc, eccen, eccenunc, prad, pradunc
def ksasData(fields=["kepid"],ksasFile=defaultKSASfile):
	data=open(ksasFile)
	lines = data.readlines()
	ksasDict={}
	headers = string.replace(lines[30],"def2","").split(",")
	for line in lines[33:]:
		elems=line.rstrip().split(",")
		# ditch the .01 so the indices match later
		shortKOI= elems[0][:6]
		ksasDict[shortKOI]={}
		for field in fields:
			fieldPos=gb.position(headers,field)[0]
	#		print field, fieldPos
			ksasDict[shortKOI][field]=elems[fieldPos]
	return ksasDict
	

########### Get corresponding KFOP ID for KOI number
### Step 1: go to KFOP
### Step 2: save the current ACTIVE and INACTIVE .html files (NOT the exported bit, the actual .html)
### Step 3: combine them into one file, e.g. targets_all_20120730.html
def getKFOPidDict():
	data = open(kfopIDtargetFile)
	lines = data.readlines()
	data.close()
	koi = "NA"
	nextLine = False
	idDict = {}
	for nn,line in enumerate(lines):
		# First figure out what KOI we're working with
		try:
			first = line[0:6] 
			if first[0] == "K":
				koi = first
				nextLine = nn+3
		except:
			nothing=0
		# Next, check if you are on one of the lines with the ID in it
		if nn == nextLine:
			elems = line.split(",")
			idNum = string.replace( string.replace(elems[0], "('view_fchart.php?id=",""), "'","")
			idDict[koi]=idNum
	return idDict


	
############ TEST AREA ##########

#foo = ksasData(["kepid","posglon","posglat", "kpmag"])
#print foo["K00005"]	