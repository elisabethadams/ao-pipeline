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

import os
import string

## local packages
import aries
import grabBag as gb

##### Definitions
### Pick which night to use
useNight = "20111008"
allNights = aries.framesForNights.keys()

nightPath = ao.dataDir + useNight + "/"

def cleanse(obj,toUpper=False):
	for char in ["_"," ","/"]:
		obj = string.replace(obj,char,"")
	if toUpper:
		return string.upper(obj)
	else:
		return obj

## all files in that directory
allFiles = os.listdir(nightPath)
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
			exp= cleanse(ao.getStuffFromHeader(nightPath+ff,"EXPTIME"))
			filt = cleanse(string.replace(ao.getStuffFromHeader(nightPath+ff,"FILTER"),"band", ""))
			obj = cleanse(ao.getStuffFromHeader(nightPath+ff,"OBJECT"),toUpper=True)
			## Create dictionary of objects by object, filter	
			if (obj, filt) not in allObjDict.keys():
				#print "New object, filter:",obj, filt
				allObjDict[obj,filt] =[ff]
			else:
				allObjDict[obj,filt].append(ff)
			## Finally, make list of all frames by filter for each night
			num = int(ff[7:11])
			for nn in allNights:
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



## Print targets to lists based on filters, exptimes
#print "Creating lists of skies with ",len(allSkiesByExp.keys())," exposures..."
##print "Keys:",allSkiesByExp.keys()
#for exp in allSkiesByExp.keys():
#	g=open(nightPath+"allSkyD_"+exp+".txt","w")
#	#print exp, len(allSkiesByExp[exp])
#	for ff, obj in allSkiesByExp[exp]:
#		print >>g, ff
#	g.close()

## Print darks to lists based on exptimes
#print "Creating lists for darks with ",len(allDarkDict.keys())," exposures..."
##print "Keys:",allDarkDict.keys()
#for exp in allDarkDict.keys():
#	g=open(nightPath+"allDark_"+exp+".txt","w")
#	#print exp, len(allDarkDict[exp])
#	for ff in allDarkDict[exp]:
#		print >>g, ff
#	g.close()
	
## Print skys to lists based on exptimes, filters
#print "Creating lists for skies with ",len(allSkyDict.keys())," filters..."
##print "Keys:",allSkyDict.keys()
#for filt in allSkyDict.keys():
#	g=open(nightPath+"allSky_"+filt+".txt","w")
#	#print filt, len(allSkyDict[filt])
#	for ff in allSkyDict[filt]:
#		print >>g, ff
#	g.close()

## Print lists for each object and filter
#print "Creating lists for targets with ",len(allObjDict.keys())," objects..."
##print "Keys:",allObjDict.keys()
#for obj,filt in allObjDict.keys():
#	g=open(nightPath+"allObj_"+obj+"_"+filt+".txt","w")
#	#print obj, filt, len(allObjDict[obj,filt])
#	for ff in allObjDict[obj,filt]:
#		print >>g, ff
#	g.close()


## Print lists for each night and filter
print "Creating lists for targets with ",len(nightAndFilterDict.keys())," filters and nights..."
#print "Keys:",nightAndFilterDict.keys()
for nn,filt in nightAndFilterDict.keys():
	g=open(nightPath+nn+"_"+filt+".txt","w")
	#print obj, filt, len(nightAndFilterDict[nn,filt])
	for ff in sorted(nightAndFilterDict[nn,filt]):
		print >>g, ff
	g.close()
