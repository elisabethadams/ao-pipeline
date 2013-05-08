#!/usr/bin/env python
#
# Step 8 of AO compilation pipeline: find detection limits
#     Prereqs:
#       0. run step4-getmag.py (makes OBJECT_Filt.fits.mag, assumed to exist)
#     This script will:
#       1. create a directory including all the files you need to make the tar file for KFOP
#       2. make the .tar archive (FROM INSIDE THE DIRECTORY, NOT OUTSIDE: NO NESTED DIRECTORIES ALLOWED!)

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


### Other settings
copyDataFiles=True
makeObservingSummary=True
closeDist = 10.0 # arcsec

### Format of file name is determined by
### https://kfop.ipac.caltech.edu/files/website/Bulk_File_Upload_Instructions_v3.pdf
date = string.replace(str(datetime.datetime.now())[:10],"-","")

####################### CHECK THIS! #############################
## You must use a new number every time you try (and fail) to upload per day
## See KFOP for revised directions
batchNum= "-001"
## Your initials may not be "ea"
tarShortName = "ea-"+date+batchNum

obsNotesTarShortName = "obsnotes-"+date+batchNum
tarFileName = tarShortName +".tar"
tarFileContentsName = tarShortName +".txt"
################################################################


## Import settings files
## Implicit assumption we are using ARIES data. But then, why would we be uploading other people's data?
settings={}; nightForKOI=[]
for koi in useObjects:
	settings[koi]={}
	settings[koi]=ao.readSettingsFile(ao.settingsFile(koi))
	if ( (settings[koi]['Plate_scale_Ks'] == '0.02') | (settings[koi]['Plate_scale_Ks'] == '0.02085')):
		settings[koi]["Mode"]="F/30"
	else:
		settings[koi]["Mode"]="F/15"
		

## Step 1: Create tar directory
mainBatchDir = ao.mainDir+"batches/"
batchDir = mainBatchDir+tarShortName+"/"
obsNotesBatchDir = mainBatchDir + obsNotesTarShortName+"/"

print tarFileName, "will contain the .tar archive of files"
print batchDir+tarFileContentsName, ": text listing of files, brief description"


if os.path.exists(batchDir):
	os.system("rm -f "+batchDir+"/*")
else:
	os.makedirs(batchDir)	
if os.path.exists(obsNotesBatchDir):
	os.system("rm -f "+obsNotesBatchDir+"/*")
else:
	os.makedirs(obsNotesBatchDir)	

### Figure out which koi have J and or K data
koiDict = {}
for filt in filters:
	koiDict[filt]=[]
	for obj in useObjects:
		if os.path.isfile(ao.koiFilterDir(obj,filt) + ao.finalKOIimageFile(obj,filt)):
			koiDict[filt].append(obj)

print "\nThese files have J data:"
print koiDict["J"]
print "\nThese files have Ks data:"
print koiDict["Ks"]

# we will need to rename: Ia means imaging-AO
def getBatchName(koi,filt,suffix):
	return koi+"Ia-ea"+settings[koi]["Night"]+filt+suffix

# Open text file to go with each file in the tar file
g = open(batchDir+tarFileContentsName,'w')

## Now copy
for filt in filters:
	for koi in koiDict[filt]:
		if (koi in useObjects) & (copyDataFiles == True):
			print koi,filt, "ref frame=",settings[koi]["RefFrame_"+filt]
			# Values we want: FOV
			fov = 1024.*eval(settings[koi]["Plate_scale_"+filt])
			fitsFile = ao.koiFilterDir(koi,filt)+ao.finalKOIimageFile(koi,filt)
			# Copy final FITS file
			fitsFileShortName = getBatchName(koi,filt,".fits")
			os.system("cp "+fitsFile+" "+batchDir+fitsFileShortName)
			print >>g, fitsFileShortName,"ARIES AO FITS image in "+filt+" with "+str(int(fov))+"\" FOV"			
	##   	# Copy png finder chart
	##   	pngFileShortName = getBatchName(koi,filt,".png")
	##   	os.system("cp "+ao.plotDir+"finders/finder_"+koi+"_"+filt+".png"+" "+batchDir+pngFileShortName)
	##   	print >>g, pngFileShortName, "ARIES AO image in "+filt+" with "+str(int(fov))+"\" and 4\" FOVs"			
			# Copy limiting magnitudes
			limFileShortName = getBatchName(koi,filt,"lim.tsv")
			os.system("cp "+ao.koiFilterDir(koi,filt)+ao.finalKOIimageFile(koi,filt)+"_lim.tsv"+" "+batchDir+limFileShortName)
			getBatchName(koi,filt,".png"),"\t","ARIES AO image in "+filt+" with "+str(int(fov))+"\" FOV"
			print >>g, limFileShortName, "ARIES AO magnitude limits vs. distance in "+filt


## Get more details for long summary:
initSigma=5.
longtext={}
for filt in filters:
	for koi in koiDict[filt]:
		longtext[koi,filt] =""
		if (koi in useObjects) & (makeObservingSummary == True):
			fitsFile = ao.koiFilterDir(koi,filt)+ao.finalKOIimageFile(koi,filt)
			cooFile = fitsFile+".coo"
			cooFileFull = fitsFile+".fullcoo"
			if os.path.isfile(cooFile):
				data=open(cooFile)
				lines = data.readlines()
				elems=lines[0].rstrip().split(" ")
				initX=eval(elems[0])
				initY=eval(elems[1])
			#	print cooFile,initX,initY
				moffatFWHM= ao.getFWHMfromFITScoo(fitsFile,cooFile)
				fwhm = eval(moffatFWHM)
#				xVal, yVal, xWidth, yWidth, height=gaussian.returnFWHMaroundTarget(fitsFile,initX,initY,initSigma)
#				fwhm = max(xWidth, yWidth)
			#	print koi,filt,round(fwhm,2)
				seeing = fwhm * eval(settings[koi]["Plate_scale_Ks"])
			#	print koi,fwhm, seeing, eval(settings[koi]["Plate_scale_Ks"])
				longtext[koi,filt,"seeing"] = seeing
		else:
				print cooFile, " does not exist"
				longtext[koi,filt,"seeing"] = "NA"
				
# Long text for summary

### What ID # on KFOP corresponds to the KOI?
idDict = kepler.getKFOPidDict()

#### If the format of how KFOP data is changed considerably, this will have to change too
def linkForFile(koi,filt,ext):
	useID = idDict[koi].rstrip()
	return "<a target=\"_blank\" href=https://kfop.ipac.caltech.edu/files/target"+useID+"/Images/"+getBatchName(koi,filt,ext)+">"+filt+"</a>"


### Function to create the text for each object under observing notes	
### https://kfop.ipac.caltech.edu/files/website/ObsNotes_Bulk_Upload_Instructions.pdf


def obsNotesForKOI(koi):
	#print settings[koi]
	if ((koi in koiDict["J"]) & (koi in koiDict["Ks"])):
		filtersUsed = "J and Ks"
		filterList=["J","Ks"]
		seeingText = str(round(longtext[koi,"J","seeing"],2))+"\" in J and "+str(round(longtext[koi,"Ks","seeing"],2))+"\" in Ks."
		fov = 1024.*eval(settings[koi]["Plate_scale_Ks"])
		limitsLinkText = linkForFile(koi,"Ks","lim.tsv") + ", " + linkForFile(koi,"J","lim.tsv")
##		imageLinkText = "PNG images: "+linkForFile(koi,"Ks",".png") + ", " + linkForFile(koi,"J",".png") + "\nFITS images: " + linkForFile(koi,"Ks",".fits") + ", " + linkForFile(koi,"J",".fits")
		imageLinkText = "\nFITS images: " + linkForFile(koi,"Ks",".fits") + ", " + linkForFile(koi,"J",".fits")
		

	elif (koi in koiDict["Ks"]):
		filtersUsed = "Ks"
		filterList=["Ks"]
		fov = 1024.*eval(settings[koi]["Plate_scale_Ks"])
		seeingText = str(round(longtext[koi,"Ks","seeing"],2))+"\" in Ks."
		limitsLinkText = linkForFile(koi,"Ks","lim.tsv") 
##		imageLinkText = "PNG image: "+linkForFile(koi,"Ks",".png") + "\nFITS image: " + linkForFile(koi,"Ks",".fits")
		imageLinkText = "\nFITS image: " + linkForFile(koi,"Ks",".fits")
	else: # only  J
		filtersUsed = "J"
		filterList=["J"]
		fov = 1024.*eval(settings[koi]["Plate_scale_J"])
		seeingText = str(round(longtext[koi,"J","seeing"],2))+"\" in J."
		limitsLinkText = linkForFile(koi,"J","lim.tsv") 
##		imageLinkText = "PNG image: "+linkForFile(koi,"J",".png") + "\nFITS image: " + linkForFile(koi,"J",".fits")
		imageLinkText = "\nFITS image: " + linkForFile(koi,"J",".fits")

	## Does this object have additional nearby stars on the image?
	for filt in filterList:
		apertures, starn, xySkyDict, starDict = ao.readPhotMagFile(ao.koiFilterDir(koi,filt), ao.finalKOIimageFile(koi,filt), magSuffix=".mag")
		closeComps = []
		if (len(xySkyDict)>1):
			print "Found ",len(xySkyDict)," companions"
			### Okay, how close are they?
			for nn in range(2,len(xySkyDict)+1):
				distPx = math.sqrt( (eval(xySkyDict[nn][0])-eval(xySkyDict[1][0]))**2 +  (eval(xySkyDict[nn][1])-eval(xySkyDict[1][1]))**2 )
				deltaMag = eval(starDict[nn,'5.00'][3])-eval(starDict[1,'5.00'][3])
				distArcsec = eval(settings[koi]["Plate_scale_"+filt]) * distPx
				print koi, nn,distArcsec
				if distArcsec <= closeDist:
					closeComps.append([round(distArcsec,2),round(deltaMag,2)])
		else:
			print koi," has no companions"

		### Now figure out the text to output
		if closeComps == []:
			binaryText = "No companions were detected on the field of view."
		else:
			binaryText = str(len(closeComps))+" companion star(s) detected within "+str(closeDist)+"\" of the target: "
			if len(closeComps)>=1:
				for nn,comp in enumerate(closeComps):
					if (nn == len(closeComps)-1):
						post = ". "
					else:
						post = "; "
					#if comp[1] < closeDist:
					binaryText = binaryText + str(comp[1])+ " mag fainter in Ks at "+str(comp[0])+"\""+post
		
			else:
				binaryText = "No companions were detected within "+str(closeDist)+"\"."
	#	print binaryText
	
		## combine
		text = "ARIES AO observations for "+koi+" were taken on "+settings[koi]["Night"]+" in "+settings[koi]["Mode"]+" in "+filtersUsed+" (plate scale = "+settings[koi]["Plate_scale_Ks"]+"\" per pixel, FOV = "+str(round(fov,1))+"\"). The seeing was "+seeingText + " \n\n"+binaryText+"\n\nLimits on additional companions: "+limitsLinkText+"\n"+imageLinkText
		g = open(obsNotesBatchDir+koi+".txt",'w')
		print >>g, text


for koi in useObjects:	
	obsNotesForKOI(koi)


############ OKAY! LET'S ASSUME THAT ALL WENT SWIMMINGLY #############
### make observing notes tar file
os.chdir(obsNotesBatchDir)
os.system("tar -cf "+obsNotesTarShortName+".tar *")
### make data tar file
os.chdir(batchDir)
os.system("tar -cf "+tarShortName+".tar *")

