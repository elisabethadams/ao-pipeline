#!/usr/bin/env python
#
# grabBag package created 20090712 by era
# miscellaneous functions of general use

import os
import math
import numpy as np
import pylab

#### Interacting with files
def createIfAbsent(myDir):
	if not os.path.exists(myDir):
		os.makedirs(myDir)


def listToString(listOut,tab="\t"):
	return tab.join(listOut)

### Delete pre-existing file if it exists
def deleteIfPresent(file):
	try:	
		os.remove(file)
	except:
		0
		
### Read in list of sliced data 
def readListFile(listfile):
	data=open(listfile)
	lines = data.readlines()
	elemList=[]
	for line in lines:
		elems=line.rstrip()
		elemList.append(elems)
	return elemList
		
### List interactions		
def flattenList(myList):
	return [item for sublist in myList for item in sublist]	

## item position
def position(myList, value):
	return [i for i,x in enumerate(myList) if x == value]
	

# return unique items in list
# function f5 from http://www.peterbe.com/plog/uniqifiers-benchmark	
def unique(seq, idfun=None): 
	# order preserving
	if idfun is None:
		def idfun(x): return x
	seen = {}
	result = []
	for item in seq:
		marker = idfun(item)
		# in old Python versions:
		# if seen.has_key(marker)
		# but in new ones:
		if marker in seen: continue
		seen[marker] = 1
		result.append(item)
	return result
	
### String padding

def strPad(exp,roundBy,minLen,padChar=" ",padSide="right"):
	if roundBy == False:
		foo = str(exp)
	else:
		foo=str(round(exp,roundBy))
	if len(foo) < minLen:
		if padSide=="right":
			foo = foo + padChar*(minLen-len(foo))
		else:
			foo = padChar*(minLen-len(foo)) + foo			
	return foo

###### Geometry
def distanceWithErrors(x,y,xErr,yErr,verbose=False):
	xySqrSum = x**2 + y**2
	dist = math.sqrt(xySqrSum)
	if verbose:
		xSqrErr = 2*xErr*math.fabs(x)
		ySqrErr = 2*yErr*math.fabs(y)
		xySqrSumErr = math.sqrt(xSqrErr**2 + ySqrErr**2)
		print "x^2:",x**2,"y^2 err:",y**2
		print "x^2 err:",xSqrErr,"y^2 err:",ySqrErr
		print "x^2 + y^2, err:", xySqrSum, xySqrSumErr
		print "dist:",dist
	#	distErr =  dist*0.5*xySqrSumErr/xySqrSum
	distErr =  math.sqrt(x**2 * xErr**2 + y**2 * yErr**2)/dist
	return dist, distErr	

###### CDFs

def get_cdf(t, x):
	gt = np.extract(t <= x,t)
	prob = float(len(gt))/float(len(t))
	return prob

def plotCDF(data,useColor="k",thickness=0.5,useDashing="-",useLabel=""):
	yy = []
	for x in data:
		yy.append(get_cdf(data,x)) 
	pylab.plot(data,yy,color=useColor,linewidth=thickness,linestyle=useDashing,label=useLabel)


####### Plots
def thickenAxesAndTicks():
	### Now we reformat the plot to make it more legible
	ax = pylab.gca()
	## Bold labels and thick axes
	for tick in ax.xaxis.get_major_ticks():
		tick.label1.set_fontsize(14)
		tick.label1.set_fontweight('bold')
	for tick in ax.yaxis.get_major_ticks():
		tick.label1.set_fontsize(14)
		tick.label1.set_fontweight('bold')
	## Thicker tick marks !! thanks, http://www.krioma.net/blog/2010/05/tickmarks_in_matplotlib.php
	for l in ax.get_xticklines() + ax.get_yticklines(): 
	    l.set_markersize(6) 
	    l.set_markeredgewidth(1.2) 
	for l in ax.yaxis.get_minorticklines()+ax.xaxis.get_minorticklines():
		l.set_markersize(3) 
		l.set_markeredgewidth(1.2)





################################# Tests #########################################
#print distanceWithErrors(1,1,0.1,0.1)
#print "xx"+strPad(1.234,2,5)+"xx"
#print "xx"+strPad(1.2,2,5)+"xx"
#print distanceWithErrors( 254.84, 432.03, 0.0970824391947, 0.11204017136,verbose=True)

#print position([1,2,4,5,6,3,1,2],1)
#print position(["apple","fred","dfsdsf"],"apple")

#raw_data = np.array([0.9,1,1.2,2.3,3.1,3.8,4,5.4,5.5,6.1,7.8,7.9,8.1,8.4,8.5,8.05,8.55,8,9.2,10])
#data = np.sort(raw_data)
#
#plotCDF(data,useColor="b",thickness=2.5,useDashing="--",useLabel="Multiples")