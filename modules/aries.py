### aries.py: settings for ARIES AO pipeline reductions
#
#  Store definitions relate to ARIES observations
#    Generic AO-related and project functions belong in ao.py

## Modules required by this package
import ao
 
####### Which objects were observed on which nights? ###########
objectsForNight={}
objectsForNight["20091108"] = ["K00088", "K00094", "K00097", "K00098", "K00115", "K00116", "K00141", "K00153"]
objectsForNight["20100503"] = ["K00041", "K00042", "K00068", "K00069", "K00072", "K00245", "K00246", "K00260", "K00262", "K00263","K00264", "K00266", "K00269", "K00270", "K00271", "K00273", "K00274"]
objectsForNight["20100923"] = ["K00075", "K00372", "K00975"]
objectsForNight["20100925"] = ["K00013", "K00076", "K00082", "K00085", "K00257", "K00258", "K00261", "K00268", "K00974"]
objectsForNight["20111008"] = ["ABAur", "Corot-1b", "CQTau", "DGTau", "HAT-P-17b", "HAT-P-25b", "HAT-P-30b", "HAT-P-32b", "HAT-P-33b", "HAT-P-6b", "HAT-P-9b", "HD17156b", "IQAur", "K00174", "K00341","K00555", "K00638", "K00700", "K00961", "K00973", "K00979", "K01054", "K01316", "K01537", "K01883", "RWAur", "RYTau", "TrES-1b", "TTau", "WASP-1b", "WASP-2b", "WASP-33b", "XO-3b", "XO-4b"]

######## What are the "proper" object names?
allProperNamesKs = ["ABAur", "CQTau", "Corot-1b", "DGTau", "HAT-P-17b", "HAT-P-25b", "HAT-P-30b", "HAT-P-32b", "HAT-P-33b", "HAT-P-6b", "HAT-P-9b", "HD17156b", "IQAur", "K00174", "K00341", "K00555", "K00638", "K00700", "K00961", "K00973", "K00979", "K01054", "K01316", "K01537", "K01883", "RWAur", "RYTau", "TTau", "TrES-1b", "WASP-1b", "WASP-2b", "WASP-33b", "XO-3b", "XO-4b"]
allProperNamesJ = ["RYTau"]
allProperNamesFe = ["CQTau", "DGTau", "RWAur",  "RYTau"]
allProperNamesH2 = ["DGTau", "RWAur", "RYTau", "TTau"]
allProperNamesBr = ["DGTau"]

#def getProperName(obj):#
#	for nn,oo in enumerate(useObjList):
#		prefix, obj1, filt, suffix = string.replace(ff,".","_").split("_")
#		if obj1 == obj:
#			return properName[nn]
#		else:
#			print "no match", obj1, obj



######## How were the data files named (the prefix used originally, NOT including the "q")?
targetBaseName={}
nightDir = "20111008"
targetBaseName[nightDir] = "target"
nightDir = "20100923"
targetBaseName[nightDir] = "data"
nightDir = "20100925"
targetBaseName[nightDir] = "star"
nightDir = "20100503"
targetBaseName[nightDir] = "star"
nightDir = "20091108"
targetBaseName[nightDir] = "star"

######### What is the path to the data?
#def nightPathForObj(obj):
#	if night == "2011"

######## Which frames contained good data (EXCLUDE calibration data)
framesForNights={}
## 20111008 is the main directory, even though there were actually three nights of data stored here
framesForNights["night1"]=[80,475]
framesForNights["night2"]=[574,1284]
framesForNights["night3"]=[1305,2095]

framesForNights["20091108"]=[1305,2095]
framesForNights["20100503"]=[1305,2095]
framesForNights["20100923"]=[1305,2095]
framesForNights["20100925"]=[1305,2095]

######## By default we use the second frame in an object list as the reference frame
## If for some reason you want a different frame, set it below
refFrameForObj={}
refFrameForObj["K00555", "20111008"] = "qtarget0117.fits"
refFrameForObj["HAT-P-6b", "20111008"] = "qtarget0706.fits"
refFrameForObj["HAT-P-17b", "20111008"] = "qtarget0676.fits"
refFrameForObj["XO-3b", "20111008"] = "qtarget0877.fits"


## Some frames work better with a different FWHM
fwhmTypeForFrame={}
fwhmTypeForFrame["default"] = "Moffat"
fwhmTypeForFrame["HD17156b", "20111008","Ks"] = "Gaussian"
fwhmTypeForFrame["WASP-33b", "20111008","Ks"] = "Gaussian"
fwhmTypeForFrame["RWAur", "20111008","Ks"] = "Gaussian"
fwhmTypeForFrame["K00700", "20111008","Ks"] = "Direct"

## Occasionally we opt not to correct for bad pixels
doBadPixelCorr={}
doBadPixelCorr["default"] = "yes"
doBadPixelCorr["RWAur","20111008","Ks"] = "no"

## Default settings to use and misc. definitions
cr=['\n']
useFWHM = 10.
useBkg = 10.
useThresh = 100.
