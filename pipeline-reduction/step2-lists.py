#!/usr/bin/env python
#
# Step 2 of ARIES pipeline: making lists
#   BEFORE running this script, you should make sure your headers are not wrong 
#  (you may also fix the results afterwards) 
#   Also make sure that corquad.sh has finished running for all frames
#   This script will:
#    1. create a list of every target with a given filter and exposure time
#    2. create a list of every dark with a given filter
#    3. create a list of every sky with a given filter and exposure time
#    4. create a list for every object in each filter
#    5. create a list of all objects on a given night in each filter
#	Note: objects are stripped of _, " ", "/", and are uppercased

################## BEGIN PREAMBLE ###########################

import os
import sys
import string

## User packages
pipelineDir = os.path.dirname(os.path.realpath(__file__))
print "This script is stored at:",pipelineDir
moduleDir = string.replace(pipelineDir,"pipeline-reduction","modules")
print "Adding modules from:",moduleDir
sys.path.append(moduleDir) 
import ao
import aries
import grabBag as gb

### Read in which objects to use
if os.path.exists("usingDate.txt"):
	data = open("usingDate.txt","r")
	useDates = []
	lines = data.readlines()
	for line in lines:
		useDates.append(line.rstrip())
	# Only use the first one
	useNight = useDates[0]
else:
	sys.exit("I don't know what date to analyze. Please run step0-setup.py")

nightPath = ao.dataDir + useNight + "/"
base = aries.targetBaseName[useNight]
print "Night path:",nightPath, " file name base:", base
################### END PREAMBLE ############################


frameNumbers = aries.framesForNights.keys()

## list all files in the night directory
allFiles = os.listdir(nightPath)
print "\n Running through all ", len(allFiles)," files to find data..."

allObjDict={}
allSkiesByExp={}
allDarkDict={}; allDarkTimes = []
allSkyDict={}
nightAndFilterDict={}
for ff in allFiles:
	##### First check to make sure we don't include reduced fits files
	if ((ff[-5:]==".fits") & (ff[-7:]!=".d.fits") & (ff[-9:]!=".red.fits")): 
		
		##### A. Target data (all starts with 'q')
		if ff[0] == "q":
			exp= gb.cleanse(ao.getStuffFromHeader(nightPath+ff,"EXPTIME"))
			filt = gb.cleanse(string.replace(ao.getStuffFromHeader(nightPath+ff,"FILTER"),"band", ""))
			obj = gb.cleanse(ao.getStuffFromHeader(nightPath+ff,"OBJECT"),toUpper=True)
			## Create dictionary of objects by object, filter	
			if (obj, filt) not in allObjDict.keys():
				#print "New object, filter:",obj, filt
				allObjDict[obj,filt] =[ff]
			else:
				allObjDict[obj,filt].append(ff)
			## Finally, make list of all frames by filter for each night
			num = int(ff[7:11])
			for nn in frameNumbers:
				if (aries.framesForNights[nn][0] <= num <= aries.framesForNights[nn][1]):
					if (nn, filt) not in nightAndFilterDict.keys():
						nightAndFilterDict[nn,filt] =[ff]
					else:
						nightAndFilterDict[nn,filt].append(ff)


		##### B. Darks
		elif ((ff[:4] == "dark") | (ff[:4] == "Dark")):
			exp= string.replace(ao.getStuffFromHeader(nightPath+ff,"EXPTIME"), " ","")
			if exp not in allDarkTimes:
				allDarkTimes.append(exp)
				allDarkDict[exp] = []
			allDarkDict[exp].append(ff)
		##### C. Skys
		elif ((ff[:3] == "sky") & (ff[-5:]==".fits")& (ff[-7:]!=".d.fits")):
			exp= string.replace(ao.getStuffFromHeader(nightPath+ff,"EXPTIME"), " ","")
			filt = string.replace(string.replace(ao.getStuffFromHeaderao.dataDir(nightPath+ff,"FILTER"),"band", ""), " ","")
			## Create dictionary of skies by filter (for flattening)
			if filt not in allSkyDict.keys():
				allSkyDict[filt] =[ff]
			else:
				allSkyDict[filt].append(ff)
			## Also create dictionary of skies by exptime (for darks)
			if exp not in allSkiesByExp.keys():
				allSkiesByExp[exp]=[]
			allSkiesByExp[exp].append([ff,"sky"])

print "\n We found the following objects and filters:",allObjDict.keys()
print "\n We found the following sky filters:",allSkyDict.keys()
print "\n We found the following dark times:",allDarkDict.keys()
print "\n We found the following sky times:",allSkiesByExp.keys()



######## Print targets to lists based on filters, exptimes ######## 
entry = raw_input("Create lists of skies with "+str(len(allSkiesByExp.keys()))+" exposures? Type y or anything else to skip: ")

if entry == "Y":
	#print "Keys:",allSkiesByExp.keys()
	for exp in allSkiesByExp.keys():
		g=open(nightPath+"allSkyD_"+exp+".txt","w")
		#print exp, len(allSkiesByExp[exp])
		for ff, obj in allSkiesByExp[exp]:
			print >>g, ff
		g.close()

########  Print darks to lists based on exptimes ######## 
entry = raw_input("Create lists for darks with "+str(len(allDarkDict.keys()))+" exposures? Type y or anything else to skip: ")

if entry == "Y":
	#print "Keys:",allDarkDict.keys()
	for exp in allDarkDict.keys():
		g=open(nightPath+"allDark_"+exp+".txt","w")
		#print exp, len(allDarkDict[exp])
		for ff in allDarkDict[exp]:
			print >>g, ff
		g.close()

########  Print skies to lists based on exptimes, filters ######## 
entry = raw_input("Create lists for skies with "+str(len(allSkyDict.keys()))+" filters? Type y or anything else to skip: ")

if entry == "Y":
	#print "Keys:",allSkyDict.keys()
	for filt in allSkyDict.keys():
		g=open(nightPath+"allSky_"+filt+".txt","w")
		#print filt, len(allSkyDict[filt])
		for ff in allSkyDict[filt]:
			print >>g, ff
		g.close()

########  Print lists for each object and filter ######## 
entry = raw_input("Create lists for targets with "+str(len(allObjDict.keys()))+" objects? Type y or anything else to skip: ")

if entry == "Y":
	#print "Keys:",allObjDict.keys()
	for obj,filt in allObjDict.keys():
		g=open(nightPath+"allObj_"+obj+"_"+filt+".txt","w")
		#print obj, filt, len(allObjDict[obj,filt])
		for ff in allObjDict[obj,filt]:
			print >>g, ff
		g.close()

########  Print lists for each night and filter ######## 
entry = raw_input("Create lists for targets with "+str(len(nightAndFilterDict.keys()))+" filters and nights? Type y or anything else to skip: ")

if entry == "Y":
	#print "Keys:",nightAndFilterDict.keys()
	for nn,filt in nightAndFilterDict.keys():
		g=open(nightPath+nn+"_"+filt+".txt","w")
		#print obj, filt, len(nightAndFilterDict[nn,filt])
		for ff in sorted(nightAndFilterDict[nn,filt]):
			print >>g, ff
		g.close()
