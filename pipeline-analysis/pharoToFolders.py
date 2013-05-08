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

for dd in currentSubDirs:
	if dd != '.DS_Store':
		subfiles = os.listdir(pharoDir+dd)
		for ss in subfiles:
			possObj = ss[:6]
			suffix = ss[-7:]
			subFileDir = pharoDir+dd+"/"+ss
			if possObj[0] == "K": ### Very KOI prejudiced
				if os.path.exists(pharoDir+possObj) == False:
					os.makedirs(pharoDir+possObj)
				## hack because all images on this night were J
				if dd == "palomar200909_fits":
					suffix = "jt.fits"
				if suffix == "jt.fits":
					jDir = pharoDir+possObj+"/J/"
					print "dsflsdj",os.path.exists(jDir),jDir
					if os.path.exists(jDir) == False:
						print "made dir",jDir
						os.makedirs(jDir)
					shutil.copy2(subFileDir,jDir+ss)
				elif suffix == "kt.fits":	
					kDir = pharoDir+possObj+"/K/"
					if os.path.exists(kDir) == False:
						os.makedirs(kDir)
					shutil.copy2(subFileDir,kDir+ss)
				
				
##### Now it should be possible to just run the pipeline on the PHARO data. 
##### You may need to treat it separately from the ARIES stuff though.