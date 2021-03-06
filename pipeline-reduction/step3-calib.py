#!/usr/bin/env python
#
# Step 3 of ARIES pipeline: Calibration
#   BEFORE running this script, you may manually edit the target lists from Step 2
#   This script will:
#    1. combine every dark of the same exposure time into a master dark
#    2. subtract the appropriate master dark from each target list
#    3. also subtract the appropriate master dark from each sky list
#    4. combine each sky frame by filter into a master sky
#    5. divide the target data by the appropriate master sky

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

## List all files in the night directory
allFiles = os.listdir(nightPath)
## Now change to the night directory
os.chdir(nightPath)

darkExptimes=[]
for ff in allFiles:
	if ((ff[:7]=="allDark") & (ff[-1] != "~")):
		exp = string.replace(ff.split("_")[1],".txt","")
		darkExptimes.append(exp)
		darks = aries.readFileList(ff)
	### Need to add check if files exist before blithely proceeding
#		iraf.imcombine("@"+ff,"masterDark_"+exp+".fits",combine='median')

## Archive the raw darks
if not os.path.exists("raw/darks/"):
	os.system("mkdir raw/darks/")
print "An error may occur if no files match the criteria below; ignore"
os.system("mv Dark*.fits raw/darks/")
os.system("mv dark*.fits raw/darks/")


####### Now we subtract the darks from all skies
for ff in allFiles:
	if ((ff[:7] == "allSkyD") & (ff[-1] != "~")):
		elems=ff.split("_")
		exp = string.replace(elems[1],".txt","")
		# check to make sure dark exists
		if os.path.exists("masterDark_"+exp+".fits"):
			print "Subtracting darks from list",ff
			# dark subtract
	#		iraf.imarith("@"+ff,"-","masterDark_"+exp+".fits","@"+ff+"//.d")
		else:
			print "WARNING: we could not find a matching dark for exptime",exp

####### Now we combine the skies
### Note that this step allows you to make extra lists
###  (for instance, split a filter into two nights if the dark patch moved between them)
### name convention: "allSky_Ks_night1.txt" and "allSky_Ks_night2.txt"
### where night1 and night2 are whatever string you want (splits on "_")

for ff in allFiles:
	if ((ff[:7] == "allSky_") & (ff[-1] != "~")):
		elems=ff.split("_")
		filt = string.replace(elems[1],".txt","")
		if len(elems) > 2:
			extra = "_"+string.replace(elems[2],".txt","")
		else:
			extra = ""
		# now combine the skies
		print "Combining into master sky for",filt,extra
		#iraf.imcombine("@"+ff, "masterSky_"+filt+extra+".fits", combine="median", scale="mode")
		## Normalize based on the midpt, ie, median, value
		imstatOut = iraf.imstat("masterSky_"+filt+extra+".fits",fields='midpt',Stdout=1)
		median = float(imstatOut[1])
		print "normalizing by median value",median
		#iraf.imarith("masterSky_"+filt+extra+".fits","/",median,"normSky_"+filt+extra+".fits")


####### Now we flatten our data
####### NOTE: WE DO NOT DARK-SUBTRACT DATA; that is taken care of in sky-subtraction
for ff in allFiles:
	if ((ff[:6] == "allObj") & (ff[-1] != "~")):
		elems=ff.split("_")
		obj = elems[1]
		if len(elems) > 3:
			filt = elems[2]
			extra = "_"+string.replace(elems[3],".txt","")
		else:
			filt = string.replace(elems[2],".txt","")
			extra = ""
	
		# Check to make sure sky exists
		if os.path.exists("normSky_"+filt+extra+".fits"):
			print "Dividing by flat for",obj,filt
			iraf.imarith("@"+ff,"/","normSky_"+filt+extra+".fits","@"+ff+"//.red")
		else:
			print "WARNING: we could not find matching flat ","normSky_"+filt+extra+".fits"

