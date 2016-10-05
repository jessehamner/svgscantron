#!/usr/bin/python

import os
import sys
import re
import string
import argparse
import subprocess
import svgscantron as j # Jesse's functions to support the script
import datetime
import getpass
# import scantronformats as s # -

######## PROGRAM SETUP ###########

# these variables shouldn't be different among scantron sheets:
verbose=0
reallyverbose=0
#parameterfile="old4521.txt"

params = {'verbose':0, \
    'reallyverbose':0, \
    'qu':0, \
    'num':0, \
    'onlyprintanswers': 0, \
    'sheetlabel':" Only this and nothing more.", \
    'thisy':0, \
    'thisx':0, \
    'yindex':0, \
    'qu':0, \
    'num':0, \
    'parameterfile': "old4521.txt" \
    }

# This list holds qu and num:
qunum=[0,0]

onlyprintanswers = 0 # 1 for printing on the actual scantron sheet.
alph = ['A','B','C','D','E']
inputanswers="answerlist.txt"

# Very hacky -- wish there was a better way: FIXME
inkscapedict={
    'linux':["/usr/bin/inkscape","You seem to have inkscape installed"],
    'linux2':["/usr/local/bin/inkscape","You seem to have inkscape installed"],
    'linuxormac':["/opt/local/bin/inkscape","You seem to have inkscape installed"],
    'mac':["/Applications/Inkscape.app/Contents/Resources/bin/inkscape", \
    "You seem to have inkscape for Mac installed"],
    'win7':["C:/Program Files/Inkscape/inkscape.exe", \
    "You seem to have inkscape for Windows installed"]
}

# On the other hand, these variables are specific to Scantron sheet #4521
# 4.3mm seems to be right for this form, or else it's printer registration issues.
# the vertical (y) increment between rows
#yincrement=8.5 
# radius, in mm, of the answer circles:
#radius=1.6
# x1=   # 136.0

# an array of y-values for each bank of test answers:
# toplefty=[34,124.5]

# two versions of the exact same blue (a close match to the Scantron form)
#hexcolor="#5050b4"
#rgbcolor="80,80,180"

# width from the same x value in one column to the same location in the next:
#columnxincrement=29.75

# 'mark' and 'space' is a serial (UART, modem, punched-card, etc.) joke.
# but seriously, markx is the initial x-value of the struts at the bottom
# and spacex (also a joke...SpaceX... ) is the space betwen struts on the 
# RIGHT side of the form and on the BACK of the form.
#markx=131.5
#spacex=4.35

# extra space between ranks of five struts on the right side and the back:
#interspace = 3.6

########  MAIN PROGRAM: ###########

# parse the command-line options:
arguments=j.parseOptions()

# define variables based on command-line arguments:
if j.checkArguments(arguments):
    onlyprintanswers=int(arguments['onlyprintanswers'])
    params['onlyprintanswers'] = int(arguments['onlyprintanswers'])
    verbose=int(arguments['verbose'])
    params['verbose'] = int(arguments['verbose'])
    reallyverbose=int(arguments['reallyverbose'])
    params['reallyverbose']=int(arguments['reallyverbose'])
    inputanswers=arguments['answerlist']
    params['inputanswers']=arguments['answerlist']
    sheetlabel=str(arguments['sheetlabel'])
    params['sheetlabel']=str(arguments['sheetlabel'])
    parameterfile=str(arguments['inputformat'])
    params['parameterfile']=arguments['inputformat']
else:
    print("Something went wrong and the script can't continue. Sorry.")
    sys.exit()

print "***** Parameter file is %s. *****" % parameterfile

# retrieve the output file's name from the input arguments
outputfilename=j.checkOutputFile(arguments, verbose)
outputfilename=str(outputfilename + "_Scantron_KEY")
outputsvg=str(outputfilename + '.svg')
params['outputfilename']=outputfilename
params['outputsvg']=outputsvg

# check for and read in the test answer file:
answers=j.getAnswers(inputanswers, verbose)

# How many answers did you actually get?
answercount = len(answers)
params['answercount'] = answercount 

# Read in the spacing parameters from the file:
params=j.readInSheetParameters(**params) # parameterfile, params)

# if params['verbose']:
print(params)

# Let the user see that we've made it this far:
print("\n***** Creating SVG output file from the correct answer file *****\n")

# open the output file:
fo = open(outputsvg, 'w+')
params['filehandle']=fo

# figure out if we have inkscape installed 
# (don't use ImageMagick for this, folks)
inkscapepath=j.checkForInkscape(inkscapedict, params)
if inkscapepath:
    inkscapeinstalled=1
    params['inkscapeinstalled'] = 1
else:
    print "Inkscape isn't installed and you need for it to be."
    print "Continuing, but the program will only output SVG not PNG."
    inkscapeinstalled=0
    params['inkscapeinstalled'] = 0

# print(str(params['toplefty']) )
bbb = re.sub("\[|\]", "", params['toplefty'])
# print(str(bbb))

toplefty=(re.sub("\[|\]", "", params['toplefty'])).split(',')
# print(str(toplefty))

floatlist = ['circdist','radius','markx','spacex','interspace','colcount', 
'rowcount', 'y1','x1', 'yincrement', 'columnxincrement', 'pageheight', 
'pagewidth']
for key in floatlist:
    params[key]=float(params[key])

intlist = ['colcount','rowcount','yindex']
for key in intlist:
    params[key]=int(params[key])

circdist= params['circdist']
radius  = params['radius']
hexcolor= str(params['hexcolor'])
markx   = params['markx']
spacex  = params['spacex']
interspace = params['interspace']
colcount= params['colcount']
rowcount= params['rowcount']
columnxincrement=params['columnxincrement']
yincrement = params['yincrement']
yindex  = params['yindex']
y1=float(toplefty[yindex])
x1=params['x1']

# write the file header for SVG:
j.writeSVGHeader(**params)

# add the CSS section to the SVG:
j.addCSS(**params)

#if (verbose):
#    print ("\n*\tparams is: %s" % (params) ) 

# if we're printing a facsimile of the Scantron sheet, lay that down:
j.printBlueLines(**params)

if verbose:
#    print("\n\nparams is " + str(params) + '\n' )
    for thiskey in params.keys():
        print (str(thiskey))

# Start the first battery of 50 questions
qunum=j.printRowByColumn(x1,y1,colcount ,rowcount,yincrement,columnxincrement,circdist,radius,hexcolor,answers,qunum,fo,alph, onlyprintanswers,verbose,reallyverbose)

yindex=yindex+1
y1=float(toplefty[yindex]) 

# the second fifty questions; 
# restart x at 136.5 and start y at 124.5

qunum=j.printRowByColumn(x1,y1,colcount,rowcount,yincrement,columnxincrement,circdist,radius,hexcolor,answers,qunum,fo,alph, onlyprintanswers,verbose,reallyverbose)

#207 to 211 for each alignment mark.
# possibly 4mm of whitespace between each mark.
# marks are 4mm tall x 1.5mm wide

mx1=float(markx)

j.drawMark((mx1-float(spacex)), 207.5, "black", fo, onlyprintanswers,  verbose)

for s in range(0,5):
    for r in range(0,6):
        j.drawMark(mx1,207.5,"black",fo,onlyprintanswers, verbose)
        mx1 = mx1 + spacex
    
# then increment mx1 8.5mm
    mx1=mx1 + interspace


# Add some arbitrary text:
j.writeStyledText(15,8,'regular',str(str(answercount) + " question test:  " + outputfilename + ' ' + sheetlabel), fo, verbose)
# "PSCI1040.006 Test 2, Version A, Fall 2015.", fo,verbose)

# close out the SVG file
fo.write('    </g>\n</svg>')
fo.close()

# convert it to PNG:
j.convertWithInkscape(inkscapeinstalled,inkscapepath,outputfilename,verbose)


print("\n***** Done creating SVG *****\n")
# it may be beneficial to convert the PNG to PDF for printing.
