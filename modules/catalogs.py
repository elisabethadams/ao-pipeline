#!/usr/bin/env python
#
# Created 2011 Aug by era
#   Interacts with star catalogs
#     (1) 2MASS data (get coordinates for all KOIs from KFOP on 20110923)
#       use multiple sources at  http://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-dd?catalog=fp_psc
#     (2) UKIRT data (tables created by D. Ciardi 20110901 based on current active KOI list)

import sys
import string
import astLib
# User packages  
sys.path.append("/Users/era/Research/Projects/Python/modules/") 
import grabBag as gb
import ao

catalogDir = ao.infoDir + "Catalogs/"
inFile2massKOIs = catalogDir + "2mass/all_2mass_20110923_2.txt"
inFile2massTransits = catalogDir + "2mass/all_2mass_transits_20120810_verified.txt"
resultFile2massKOIs = catalogDir + "2mass/all_2mass_20110923_2_results.tbl"
resultFile2massTransits = catalogDir + "2mass/all_2mass_transits_20120814.tbl"


#################### UKIRT file ###################
# Update with newer files as they appear

inDirUKIRT = catalogDir + "UKIRT/"
readmeUKIRT = inDirUKIRT + "di-20110831.txt"
def ukirtFile(koi):
	data = open(readmeUKIRT)
	lines=data.readlines()
	for line in lines:
		elems=line.split()
		thisfile = elems[0]
		if thisfile[:6] ==koi:
			return thisfile
	data.close()
	return "DNE"

def getUKIRTmag(koi):
	useFile = ukirtFile(koi)
	data = open(inDirUKIRT+useFile)
	lines=data.readlines()
	starDict={}; nn=0
	for line in lines[19:]:
		elems=line.split()
		starDict[nn,"RA"]=elems[0]
		starDict[nn,"Dec"]=elems[0]
		starDict[nn,"Dist"]=elems[0]
		starDict[nn,"PA"]=elems[0]
		starDict[nn,"Jmag"]=elems[0]
		starDict[nn,"Jerr"]=elems[0]
		starDict[nn,"Kepmag"]=elems[0]
		starDict[nn,"d_Kepmag"]=elems[0]
		starDict[nn,"Star_Prob"]=elems[0]
		starDict[nn,"Gal_Prob"]=elems[0]
		starDict[nn,"Noise_Prob"]=elems[0]
		starDict[nn,"KIC"]=elems[0]
		starDict[nn,"KIC_dist"]=elems[0]		
	data.close()
	return starDict



###################### 2MASS ###################################

### Read in a 2MASS .tbl file (Aug 2012 format)
##  Headers:
#  |     cntr_u|             dist_x|             pang_x|             object_u|               ra_u|              dec_u|            major_u|     cntr_u|        ra|       dec|err_maj|err_min|err_ang|      designation|   j_m|j_cmsig|j_msigcom|     j_snr|   h_m|h_cmsig|h_msigcom|     h_snr|   k_m|k_cmsig|k_msigcom|     k_snr|ph_qual|rd_flg|bl_flg|cc_flg|  ndet|gal_contam|mp_flg|      j_h|      h_k|      j_k|


def read2MASStable(tableFile):
	data = open(tableFile)
	lines = data.readlines()
	data.close()
	magDict = {}
	### First figure out where the ra/dec are, because you might not always have the same columns by default
	headers=lines[73].split("|")
	nJ = 0; nJerr = 0; nK = 0;  nKerr = 0; nH = 0; nHerr = 0; nObj = 0
	for nn,hh in enumerate(headers):
		useHeader = string.replace(hh," ","")
		if useHeader == "j_m":
			nJ = nn-1
		elif useHeader =="j_cmsig":
			nJerr = nn-1
		elif useHeader == "h_m":
			nH = nn-1
		elif useHeader =="h_cmsig":
			nHerr = nn-1
		elif useHeader == "k_m":
			nK = nn-1
		elif useHeader =="k_cmsig":
			nKerr = nn-1
		elif useHeader == "object_u":
			nObj = nn-1
		elif useHeader == "dist_x":
			nDist = nn-1
			
	### There may be more than one star in 2MASS, esp. within 10"!
	inTheDict=[]
	for nn,line in enumerate(lines[77:]):
		elems = line.split()
	#	print "nJ",nJ,nJerr,elems[nJ],elems[nJerr],elems[nDist]
		lineObj = elems[nObj]
		dist = eval(elems[nDist])
		
		if lineObj in inTheDict:
			if magDict[lineObj,"dist"] > dist:
				## This object is actually closer
				useThisOne=True
			else:
				useThisOne=False
		else:
			useThisOne=True
			
		if useThisOne:
			magDict[lineObj,"dist"] = dist
			magDict[lineObj,"J"]=[elems[nJ], elems[nJerr]]
			magDict[lineObj,"H"]=[elems[nH], elems[nHerr]]
			magDict[lineObj,"Ks"]=[elems[nK], elems[nKerr]]
	
		## Now add the object to the dictionary of extant objects
		inTheDict.append(lineObj)
		
	magDict["objects"]=gb.unique(inTheDict)
	return magDict


def all2MASS():
	allDict={}
	allDict["objects"] = []
	fileNames = [resultFile2massTransits,resultFile2massKOIs]
	for ff in fileNames:
		magDict = read2MASStable(ff)
		for key in magDict.keys():
			if key == "objects":
				allDict["objects"] = allDict["objects"] + magDict["objects"] 	
			else:
				allDict[key] = magDict[key]
	return allDict


def get2MASSobjects():
	magDict=all2MASS()
	return magDict["objects"]

def getObjMag2MASS(obj,filt):
	magDict=all2MASS()
	try:
		return magDict[obj,filt]
	except:
		return ["NA","NA"]


########## Debug

#testObj = get2MASSobjects()
#print len(testObj)
#
#		
#testObj = ["K00115","K01537","HAT-P-6b","CoRoT-1b"]
##
#for obj in testObj:
#	print obj, "J", getObjMag2MASS(obj,"J"), "Ks", getObjMag2MASS(obj,"Ks")





####### Create 2MASS catalog file #######

### Read in exoplanet dump from exoplanet.eu 
## NOTE: I changed the default .csv file so it has no spaces in the planet names
##       Also, and this is their misunderstanding of the spirit of "csv", I got rid of the commas in the molecules
##        so that "CO2,H2O" ---> "CO2_H2O"
def readInExoplanetCatalog(exoCat):
	data=open(exoCat,"r")
	lines = data.readlines()
	data.close()
	exoDict={}
	exoDict["objects"] = []
	for line in lines[1:]:
		elems=line.split(",")
		obj = string.replace(elems[0]," ","")
		raString = elems[16]
		decString = elems[17]
		exoDict[obj] = [raString, decString]
		exoDict["objects"].append(obj)
#	print "found objects:",len(exoDict["objects"])
	return exoDict


### Output VO table of KOIs that can be used by 2MASS 
def outputVOtableFor2MASS(output2MASSfile,useDict="exoplanet.eu"):
	print "Printing to...", output2MASSfile
	out = open(output2MASSfile,"w")
	print >>out, "|   object   |   ra          |   dec         |  major       |"
	print >>out, "|   char     |   double      |  double       |  double      |"
	
	if useDict=="exoplanet.eu":
		exoDict = readInExoplanetCatalog(catalogDir+"exoplanet.eu/exoplanet.eu_catalog_20120810.csv")
		objects = exoDict["objects"]
	else:
		print "I'm sorry, I don't know how to deal with that object info input:", exoDict
		return
	
	for obj in objects:
		raString = exoDict[obj][0]
		decString = exoDict[obj][1]
#		print obj, raString,decString
		raDec = str(astLib.astCoords.hms2decimal(raString, ":"))+"  "
		decDec = str(astLib.astCoords.dms2decimal(decString, ":"))+"  "
		if ((raDec != "0.0  ") & (decDec != "0.0  ")):
		#	print obj, raString, "xx",raDec,"xx", decString, decDec
			if len(raDec) < 16:
				raDec = raDec + " "*(16-len(raDec))
			if len(decDec) < 16:
					decDec = decDec + " "*(16-len(decDec))
			##### We assume the positions are good to within 2"
			print >>out, obj+"         "+raDec+" "+decDec+" 2.0"
	out.close()

