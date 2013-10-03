#!/usr/bin/env python
#
# Put PHARO images into folders just like ARIES, so pipeline-analysis can work

import sys
import os
import string
import shutil

# User packages
pipelineDir = os.path.dirname(os.path.realpath(__file__))
moduleDir = string.replace(pipelineDir,"pipeline-analysis","modules")
sys.path.append(moduleDir) 

import ao

pharoDir = ao.objDirByInstr("PHARO")

currentSubDirs = os.listdir(pharoDir)

##### Some of the files have DUPLICATES (18, 284, 271). Here are the files we used:
filesUsedAOI = "authoritative_list_ao1.txt"
g = open(filesUsedAOI)
lines = g.readlines()
g.close()
usedThese=[]
for line in lines:
	usedThese.append(line.rstrip())

print usedThese

for dd in currentSubDirs:
	if dd != '.DS_Store':
		subfiles = os.listdir(pharoDir+dd)
		for ss in subfiles:
			possObj = ss[:6]
			suffix = ss[-7:]
			subFilePath = pharoDir+dd+"/"+ss
			if ss in usedThese: 
				if os.path.exists(pharoDir+possObj) == False:
					os.makedirs(pharoDir+possObj)
				## hack because all images on this night were J
				if ((dd == "palomar200909_fits") & (suffix[-5:] == ".fits")):
					suffix = "jt.fits"
				### Copy and rename files to subdirectories
				if suffix == "jt.fits":
					jDir = pharoDir+possObj+"/J/"
					if os.path.exists(jDir) == False:
						print "made dir",jDir
						os.makedirs(jDir)
					shutil.copy2(subFilePath, jDir+possObj+"_J.fits")
#					if possObj in ["K00018","K00271","K00284"]:
#						print "copied fits file"
					if os.path.exists(subFilePath +".coo"):
						shutil.copy2(subFilePath +".coo", jDir+possObj+"_J.fits.coo")
					if os.path.exists(subFilePath +".mag.1"):
						shutil.copy2(subFilePath +".mag.1", jDir+possObj+"_J.fits.mag")
#						if possObj in ["K00018","K00271","K00284"]:
#							print "copied mag file"
				elif suffix == "kt.fits":
					kDir = pharoDir+possObj+"/K/"
					if os.path.exists(kDir) == False:
						os.makedirs(kDir)
					shutil.copy2(subFilePath, kDir+possObj+"_Ks.fits")
					if possObj in ["K00018","K00271","K00284"]:
						print "copied fits file"
					if os.path.exists(subFilePath +".coo"):
						shutil.copy2(subFilePath +".coo", kDir+possObj+"_Ks.fits.coo")
					if os.path.exists(subFilePath +".mag.1"):
						shutil.copy2(subFilePath +".mag.1", kDir+possObj+"_Ks.fits.mag")
				
				
##### Now it should be possible to just run the pipeline on the PHARO data. 
##### You may need to treat it separately from the ARIES stuff though.
