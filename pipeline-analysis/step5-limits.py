#!/usr/bin/env python
#
# Step 6 of AO compilation pipeline: make tables
#     Prereqs:
#       0. run step3-findlimits.py (makes OBJECT_Filt.fits_lim.tsv, assumed to exist in this script)
#     This script will:
#       1. make a table of all objects and limits from 0.1"-4"
#       2. make plot of companions vs. distance with limits overlaid

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
fwhmDict={}
for obj in useObjects:
	settings[obj]={}
	settings[obj]=ao.readSettingsFile(ao.settingsFile(obj,instr=instrUsed))
	## Import fwhm from stars file
	starInfo=ao.readStarsFile(ao.starsFile(obj,instr=instrUsed),delimiter="\t")
	for filt in filters:
		fwhmDict[obj,filt] = "NA"
		for xx in starInfo:
			if xx[0] == filt:
				fwhmDict[obj, filt] = xx[2]

#print fwhmDict

################### END PREAMBLE ############################


#### Import limiting mag files
bigDict={}; byApDict={}; allApsForObj={}; byApDictKepMag = {}
for filt in filters:
	for obj in useObjects:
	#	print "reading limits for",obj
		arcsec=[];mags=[];kepMags=[]
		fitsFile=ao.koiFilterDir(obj,filt,instrUsed)+ao.finalKOIimageFile(obj,filt,instrUsed)
		magFile=fitsFile+"_lim.tsv"
	#	print magFile
		if os.path.isfile(magFile):
			deltaMagDict = ao.importLimitingMagFile(magFile)
			allApsForObj[obj] = deltaMagDict["annuli"]
			sortedKeys=[]
			for key in deltaMagDict["annuli"]:
				#print key, obj, deltaMagDict[key]
				arcsec.append(key)
				mags.append(deltaMagDict[key])
				kepMags.append(deltaMagDict[key,"KepMag"])
				byApDict[obj,filt,key] = deltaMagDict[key]
				byApDict[obj,filt,key,"KepMag"] = deltaMagDict[key,"KepMag"]
			#print mags, arcsec
			bigDict[obj,filt] = mags
			bigDict[obj,filt,"KepMag"] = kepMags


########## Import dictionary from KSAS #############
ksasDict = kepler.ksasData(["kepid","posglon","posglat", "kpmag","jmag","kmag"])


##################################### Output table ################################
## Table showing limits
def makeTable(useFilter,objectList=[],extra="",doAllTheAps=False,alsoShowKepMags=False):
	if objectList==[]:
		objectList=useList[useFilter]
	magSummaryFile=ao.mainDir+"tables/limitingMagSummary_"+useFilter+extra+".tsv"
	magSummaryFileTex= string.replace(magSummaryFile, ".tsv", ".tex")
	print "\nWriting summary of limits to file:",magSummaryFile
	g = open(magSummaryFile,'w')
	gTex = open(magSummaryFileTex,'w')
	if useFilter == "all":
		ourFilters = filters
	else:	
		ourFilters = [filt]
	#### The full set of apertures run makes for a very wide table
	if doAllTheAps:
		specialAps=allApsForObj[objectList[0]] ### implicitly assumes same aps used for all objects; this table gets weird otherwise
		print "\n\n",specialAps,"\n\n"
		print >>g, "\t".join(["Object", "Instr", "Filter", "Target_Mag",  "FWHM"]) + "\t" + "\t".join(specialAps)
		print >>gTex,"\t &".join(["Object", "Instr", "Filter", "Target_Mag", "FWHM"]) + "\t" + "\t &".join(specialAps) + "\\\\"	
	#### A subset of apertures is preferable for published tables
	else:
		specialAps=["0.1","0.2","0.5","1.0","2.0","4.0"]
		print >>g, "\t".join(["Object", "Instr-Filter", "Target_Mag", "FWHM","0.1\"","0.2\"","0.5\"","1.0\"","2.0\"","4.0\""])
		print >>gTex,"\t &".join(["Object", "Instr-Filter", "Target_Mag", "FWHM", "0.1\"","0.2\"","0.5\"","1.0\"","2.0\"","4.0\"","\\\\"])	
	for obj in objectList:
		for filt in ourFilters:
			if fwhmDict[obj,filt] == "NA":
				print "No data for:",obj, filt
			else:
				### Print apertures
				### Print 2MASS magnitudes
				if settings[obj]["2MASS_"+filt]=="XX":
					mag2MASS = "NA"
				else:
					mag2MASS =  str(eval(settings[obj]["2MASS_"+filt])[0])
				print >>g, "\t".join( gb.flattenList([[obj, instrUsed+"-"+filt, mag2MASS, str(fwhmDict[obj,filt]) ]])),
				print >>gTex, "\t &".join( gb.flattenList([[obj, instrUsed+"-"+filt, mag2MASS, str(fwhmDict[obj,filt]) ]])),
				### Print limits
				for ap in specialAps:
				#	print "ap",ap,fwhmDict[obj,filt]
					if eval(ap) >= eval(fwhmDict[obj,filt]):
					#	print "..."
						print >>g, "\t",round(byApDict[obj,filt,ap],2), 
						print >>gTex, "\t&", round(byApDict[obj,filt,ap],2),
					else:
						print >>g, "\t -- ",
						print >>gTex, "\t& -- ",
				## be sure to close the line
				print >>g, ""
				print >>gTex, "\\\\"
				#### This prints the Kepler-mag limits directly underneath the J/Ks limits
				if alsoShowKepMags:
					### get the target's Kepler mag
					try:
						kepMag = eval(ksasDict[obj]["kpmag"])
					except:
						kepMag = "--"
					### remember to subtract from the limits (absolute, not relative)
					
					print >>g, "\n",obj+"\t",instrUsed+"-"+filt+"toKp \t  ",kepMag, "\t", str(fwhmDict[obj,filt]),
					print >>gTex, "\n",obj+"& ",instrUsed+"-"+filt+"toKp &  ",kepMag, "\t", str(fwhmDict[obj,filt]),
					for ap in specialAps:
					#	print "ap",ap,fwhmDict[obj,filt]
						if eval(ap) >= eval(fwhmDict[obj,filt]):
							if kepMag == "--":
								print >>g, "\t",byApDict[obj,filt,ap,"KepMag"],
								print >>gTex, "\t&", byApDict[obj,filt,ap,"KepMag"],
							else:
								print >>g, "\t",round(byApDict[obj,filt,ap,"KepMag"] - kepMag, 2), 
								print >>gTex, "\t&", round(byApDict[obj,filt,ap,"KepMag"] - kepMag, 2),
								
						else:
							print >>g, "\t -- ",
							print >>gTex, "\t& -- ",
				## be sure to close the line
				print >>g, ""
				print >>gTex, "\\\\"
	print "\nCreated file:",magSummaryFile
	print "\nCreated file:",magSummaryFileTex
	g.close()


############################ YOU MAY WANT TO KEEP SEVERAL OPTIONS BELOW FOR DIFFERENT SUBSETS ############################

##### Make tables of ALL objects
#makeTable("J")
#makeTable("Ks")

######## For paper AO II -- 2011 ARIES data ##########
#### Table I
#nonKeplerObj = ["Corot-1b", "HAT-P-17b", "HAT-P-25b", "HAT-P-30b", "HAT-P-32b", "HAT-P-33b", "HAT-P-6b", "HAT-P-9b", "HD17156b", "TrES-1b", "WASP-1b", "WASP-2b", "WASP-33b", "XO-3b", "XO-4b"]
#makeTable("Ks",objectList=nonKeplerObj,extra="aoII")

#makeTable("Ks",objectList=["K00094"],extra="_K00094")
#makeTable("J",objectList=["K00094"],extra="_K00094")

#makeTable("Ks", objectList =['K00174', 'K00341', 'K00555', 'K00638', 'K00700', 'K00961', 'K00973', 'K00979', 'K01054', 'K01316', 'K01537', 'K01883'], extra="_aoIIK")

#makeTable("Ks", objectList =['K00174', 'K00341', 'K00555', 'K00638', 'K00700', 'K00961', 'K00973', 'K00979', 'K01054', 'K01316', 'K01537', 'K01883', 'Corot-1b', 'HAT-P-17b', 'HAT-P-25b', 'HAT-P-30b', 'HAT-P-32b', 'HAT-P-33b', 'HAT-P-6b', 'HAT-P-9b', 'HD17156b', 'TrES-1b', 'WASP-1b', 'WASP-2b', 'WASP-33b', 'XO-3b', 'XO-4b'], extra="_aoII")

### For paper I erratum
objectsARIESaoI = ["K00013","K00041","K00042","K00068","K00069","K00072","K00075","K00076","K00082","K00085","K00088","K00094","K00097","K00098","K00115","K00116","K00141","K00153","K00245","K00246","K00257","K00258","K00260","K00261","K00262","K00263","K00264","K00266","K00268","K00269","K00270","K00271","K00273","K00274","K00372","K00974","K00975"]
#makeTable("Ks", objectList = objectsARIESaoI, doAllTheAps = True, extra="_aoIerrA")
#makeTable("J", objectList = objectsARIESaoI, doAllTheAps = True, extra="_aoIerrA")
objectsPHAROaoI = ["K00005","K00007","K00008","K00010","K00011","K00013","K00017","K00018","K00020","K00022","K00028","K00041","K00064","K00068","K00069","K00070","K00072","K00075","K00084","K00087","K00092","K00098","K00102","K00103","K00104","K00106","K00108","K00109","K00111","K00112","K00113","K00117","K00118","K00121","K00122","K00123","K00124","K00126","K00127","K00137","K00148","K00153","K00180","K00244","K00247","K00249","K00251","K00263","K00265","K00271","K00275","K00281","K00283","K00284","K00285","K00292","K00303","K00306","K00313","K00316","K00364","K00365","K00377"]
#makeTable("J", objectList = objectsPHAROaoI, doAllTheAps = True, extra="_aoIerrP")
#makeTable("Ks", objectList = objectsPHAROaoI, doAllTheAps = True, extra="_aoIerrP")

makeTable("all", objectList = useObjects, doAllTheAps = False, extra="_aoIerr"+instrUsed,alsoShowKepMags=True)

