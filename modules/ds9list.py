#!/usr/bin/env python
#
# Created 2010-12-17 by era
# Displays a list of fits files into the same ds9 window
# Must be in same directory as list, fits files

import sys
import os
import string

#for arg in sys.argv:
#    filename=arg

args = sys.argv

filename = args[1]

print args, len(args)

if len(args) >= 3:
	suffix = "."+args[2]+".fits"
else:
	suffix = ".fits"
print suffix

datafile = open(filename)

lines = datafile.readlines()
command = "ds9 -zscale -zoom 0.5"
for line in lines:
	modline=string.replace(line,".fits",suffix)
	command = command +" " + modline.rstrip()
datafile.close()


command = command +" -single &" 

print command

os.system(command) 



