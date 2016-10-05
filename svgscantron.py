#!/usr/bin/python

# svgscantron.py: a module for writing properly formatted scantron answer sheets
# using output from a LaTeX compile (or any other CR-separated integer data source)
#
# The formatting only supports one particular scantron form at this time. 
# 
#
# Version 0.2
# October 2015
# Jesse Hamner
# j h a m n e r  at  gee mail period com
#
#

import os
import sys
import re
import string
import argparse
import subprocess
import datetime
import getpass
import io

def readInSheetParameters(**params):
    filename = params['parameterfile']

    if (params['reallyverbose']):
        print "reading in parameters from %s" % filename
        print "parameters thus far are: " % params

    fileobject = open(filename, 'r')
    fi = fileobject.read()
    fs=fi.rstrip().split('\n')
    for i in fs:
#        print str(i)
        if (re.search("^#", i) ) :
            continue
        if (re.search("^\s*$", i) ) :
            continue
        i=re.sub('\s*=\s*','\t', i)
#        print(str(i))
        [j,k]=i.split('\t')
        j=j.rstrip()
        k=k.rstrip()
#        print(str(j) + ':' + str(k) )

        params[j]=k
    return (params)


def printRowPartTwo(*args, **params):
    qu=params['qu']
    num=params['num']
    params['thisx']=0
    params['thisy']=0
    answers=args[1]
    columnxincrement=params['columnxincrement']
    print(str(answers))

    yincrement=float(params['yincrement'])
    thisx=float(params['x1'])
    columnxincrement=float(params['columnxincrement'])
    
    for col in range(0,int(params['colcount']) ):
        thisy=float(params['y1'])
        for y in range(0,int(params['rowcount'])):
            num=num+1
            
            try:
                answers[qu]
            except:
                answers.append(-9)
            drawFive( )
            thisy=thisy+yincrement
            qu=qu+1
        thisx=thisx+columnxincrement
    filehandle.write("<!-- question counter is " + str(qu) + "  -->\n")
    
    params['qu']=qu
    params['num']=num   
 
    return params

# array is a list of [qu, num]
def printRowByColumn(x1, y1, colcount, rowcount,yincrement, columnxincrement, circdist, radius, hexcolor, answers, array, filehandle, alph, onlyprintanswers, verbose, reallyverbose):
    qu=array[0]
    num=array[1]
    yincrement=float(yincrement)
    thisx=float(x1)
    columnxincrement = float(columnxincrement)

    for col in range(0,colcount):
        thisy=float(y1)
        for y in range(0,rowcount):
            num=num+1
        
            try:
                answers[qu]
            except:
                answers.append(-9)
#                   x,   y, xincrement, radius, color, correct,   number, verbose
            drawFive(thisx,thisy, circdist, radius, hexcolor, answers[qu],num,filehandle, alph, onlyprintanswers,verbose, reallyverbose)
            thisy=thisy + yincrement
            qu=qu+1
        thisx=thisx+columnxincrement
    
    filehandle.write("<!-- question counter is " + str(qu) + "  -->\n")
    array=[qu,num]
    return array

def checkArguments(arguments):
    print (str(arguments))

    try:
        onlyprintanswers=int(arguments['onlyprintanswers'])
        if (onlyprintanswers==0):
            print("onlyprintanswers equals " + str(onlyprintanswers) + \
            "; the script will print the whole sheet." )
        elif (onlyprintanswers==1):
            print("onlyprintanswers equals " + str(onlyprintanswers) + \
            "; the script will print only the answer circles." )
        else:
            print("The variable indicating whether the script should print " + \
            "only filled circles has an error.")
            sys.exit()
    except:
        print("Something went wrong with parsing the program arguments, at " + \
        "least the 'onlyprintanswers' argument.")
        sys.exit()

    try:
        verbose=int(arguments['verbose'])
#    print('verbose equals ' + str(verbose))
        if (verbose==1):
            print "verbose is set to TRUE."
        elif (verbose==0):
            print "verbose is set to FALSE."
        else:
            print "We shouldn't be here! verbose should have an answer."
            sys.exit()
    except:
        print "verbose is undef and caused an exception; that's a problem."
        sys.exit()

    try:
        reallyverbose=int(arguments['reallyverbose'])
        if (reallyverbose==0):
            print("reallyverbose is set to FALSE.")
        elif (reallyverbose==1):
            print("reallyverbose is set to TRUE.")
        else:
            print("The variable indicating 'really verbose' status is not " + \
            "behaving correctly. You should fix it.")
            sys.exit()
    except:
        reallyverbose=0 # ill behaved but reallyverbose isn't critical right now.

    return 1

def checkOutputFile(arguments, verbose):
    try:
        outputfilename = str(arguments['outputfilename'])
        outputfilename = re.sub('\.svg', '', outputfilename)

    except:
        print("\nSomething went horribly wrong if you're seeing " + \
        "this error message.\n")
        sys.exit()
    return outputfilename

def writeSVGHeader(**params): # width="279.5mm", height="216.2mm", verbose):
# write the file header for SVG:

    try:
        height= params['pageheight']
    except:
        height=216.2 # assumes landscape, not portrait

    try:
        width= params['pagewidth']
    except:
        width=279.5 

    header='''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
    <svg xmlns="http://www.w3.org/2000/svg" width="%smm" height="%smm"  >
    <g id="main">''' % (width,height)

    try:
        params['filehandle'].write(header + '\n' )
        return 1
    except:
        print "WARNING COULD NOT WRITE TO OUTPUT FILE!\n\n"
        sys.exit()
        return 0

# make css:
def addCSS(**params): #rgbcolor="80,80,180", verbose):
    try:
        rgbcolor=params['rgbcolor']
    except:
        rgbcolor="80,80,180"

    try:
        if (params['verbose']):
            print "rgbcolor set to %s" % rgbcolor
    except:
        print "something went wrong with assigning rgbcolor."
        sys.exit()

    cssreal= '''
<defs>  
<style type="text/css">    
    <![CDATA[
    circle.rightanswer { 
        stroke:rgb(%s);
        stroke-width:0.1mm;
        fill:black;
    }
    circle.blank {
        stroke:rgb(%s);
        stroke-width:0.1mm;
        fill:none;
    }
    text.sizenineend {
        font-family:Arial;
        font-size:9px;
        text-anchor:end;
        fill:rgb(%s);
    }
    text.sizetenend {
        font-family:Arial;
        font-size:10px;
        text-anchor:end;
        fill:rgb(%s);
    }
    text.sizeninemiddle { 
        font-family:Arial;
        font-size:9px;
        text-anchor:middle;
        fill:rgb(%s);
    }
    line.strut {
        stroke:black;
        stroke-width:1.5mm
    }
    line.fatstrut {
        stroke:black;
        stroke-width:3mm
    }
    text.regular {
        font-size:10px;
        font-family:Arial;
        text-anchor:start;
        fill:black;
    }
    ]]>         
</style>       
</defs>   
''' % (rgbcolor, rgbcolor, rgbcolor, rgbcolor, rgbcolor)

    params['filehandle'].write(cssreal + '\n')
    return 1

def convertWithInkscape(inkscapeinstalled,inkscapepath,outputfilename,verbose):
    '''If the script has found Inkscape, convert the svg file to png. 
    Otherwise, return 0. '''
    
#pathtome=os.path.realpath(__file__)
    pathtome=os.getcwd() # NOTE this file should be in the same directory with everything else!
    outputsvg=str(outputfilename + '.svg')
    outputpng=str(outputfilename + '.png')
    

    if verbose:
        print("Path to this script is: " + str(pathtome))

    if inkscapeinstalled:
        appstring=str('"' + inkscapepath + '" ' )
        string=str(' -b ffffff -y 255 -z -d 300 --export-png="' + pathtome + "/"  +  str(outputpng) + '" ' + \
        '"' + pathtome + '/' + str(outputsvg) + '" ') 

        submit=str(appstring + string)    

        if verbose:
            print(appstring)
            print('-----------------')
            print(string)
            print('=================')
            print(submit)

        subprocess.call(submit, shell=True)

    else:
        return 0

    return 1

def parseOptions():
    if (sys.argv[0] == ""):
        print("WARNING: you need to provide a filename for the output file.")
        sys.exit()

    username=getpass.getuser()
    today=datetime.date.today()
    defaultdate=str("Sheet created by " + username  +  ", " + str(today) )
#    print(defaultdate)

    parser=argparse.ArgumentParser(description='''makesvg.py; a python script 
that converts a series of numeric multiple-choice test answers into a 
properly mapped set of Scantron answers that should print accurately 
enough to automate production of the test key.\n The script options 
require that the user add a filename from the command line using the 
"-f" option, and the user may add zero or more options, including 
verbose output, really verbose output, and a choice to print only 
the dots or the whole scantron form.

Example:

python makesvg.py -f outputsvg.svg -v \n''')

    parser.add_argument("-f", "--file", action='store', \
        dest="outputfilename", default="NONAME",
        help="provide a filename for output SVG and PNG files", metavar="FILE")

    parser.add_argument("-v", "--verbose", \
        action='store_true', dest="verbose",
        help="provide more verbose output to STDOUT", default=0 )

    parser.add_argument("-o", "--only-scantron", "--only-dots", "--dots-only", \
        action='store_true', dest="onlyprintanswers", default=0,
        help="print only the black circles needed for your answer key") 

    parser.add_argument("-vv", "--reallyverbose", \
        action='store_true', dest="reallyverbose",
        help="provide even MORE verbose output to STDOUT", default=0 )

    parser.add_argument("-a", "--answerlist", metavar="FILE", \
        action='store', dest="answerlist", default="answerlist.txt",\
        help='''provide an alternate source for the file of carriage-return 
separated integer scantron answers. The default value is 'answerlist.txt' ''')

    parser.add_argument("-l" ,"--label", metavar="TEXT", \
        action='store', dest="sheetlabel", default=defaultdate  , \
        help='''A user-specified label for the top left of the form, usually 
for identification of the test, class, semester, etc.''')

    parser.add_argument("-i", "--input-file", metavar="FILENAME", \
        action='store', dest="inputformat", default="old4521.txt", \
        help='''A user-specifed parameters file to format the location and spacing 
of the dots within the output SVG. Defaults to old4521.txt, which should be consulted
regarding the format of the input file. Other options include "pdp4521.txt".''')

    arguments = parser.parse_args()
    args = vars(arguments)
    
#    print("Looks like the input filename argument is: " + str(args['outputfilename']))

    return (args)



def __drawStub(x,y,height,width,color,filehandle,onlyprintanswers,verbose):
    '''Draw a small rectangle/line (strut) aligned with x,y specified'''
    if(onlyprintanswers):
        return 1    
    if (color=="black"):
        if (width==1.5):
            classname='class="strut"'
        if (width==3):
            classname='class="fatstrut"'
    else:
        classname='style="stroke:' + color + ';stroke-width:' + \
        str(width) + 'mm"'

    y2 = y + height
    mark = str('<line x1="' + str(x) + 'mm" y1="' + str(y) + 'mm" x2="' + \
    str(x) + 'mm" y2="' + str(y2) + 'mm" ' + classname + '/>\n')
    filehandle.write(str(mark))
    return 1

def drawFatMark(x,y,color,filehandle, onlyprintanswers,verbose):
    '''This strut is fatter than others.'''
    if(color==""):
        color="black"

    width=3
    height=4
    __drawStub(x,y,height,width,color,filehandle, onlyprintanswers, verbose)
    return 1

def drawMark(x,y,color, filehandle, onlyprintanswers, verbose):
    '''Draw a standard strut alignment mark, usually at the bottom of the page '''
    if(color==""):
        color="black"
    height=4
    width=1.5 
    __drawStub(x,y,height,width,color,filehandle,onlyprintanswers,verbose)
    return 1

def drawCircle(x,y,radius,color,correct,filehandle, verbose):
    '''Draw a circle, here one that is the Scantron answer bubble size.'''
    circletext1='<circle class="'
    circletext2='r="' + str(radius) + 'mm" '

    if correct:
        style="rightanswer"
    else:
        style="blank"

    filehandle.write(circletext1 + style + '" cy="' + str(y) + \
    'mm" cx="' + str(x) + 'mm" ' + circletext2 + '/>\n') 
    return 1

def drawFive(x,y,xincrement, radius, color,correct,number,filehandle, alph, onlyprintanswers, verbose, reallyverbose):
    '''Loop to print five empty bubbles with one filled in, plus numbers 
    and letters above the bubbles. '''        
    x=float(x)
    y=float(y)
    xincrement=float(xincrement)
    radius=float(radius)
    
    
    circletext1='<circle cy='
    circletext2='r="1.6mm" stroke="' + color + '" stroke-width="0.1mm"'
    drawNum(x,y,number,color, -3, 10, "end", filehandle, onlyprintanswers,verbose, reallyverbose)

    for i in range(0,5):
        if (i == (correct -1)):
            drawCircle(x,y,radius,color,1,filehandle,verbose)
        elif (onlyprintanswers):
            x=x+xincrement
            continue
        else:
            drawCircle(x,y,radius,color,0, filehandle, verbose)
            drawNum(x,y,(i+1), color, 0.7, 9, "end" , filehandle, onlyprintanswers, verbose, reallyverbose)

        drawNum(x, (y-3.5), alph[i], color, 0.9, 9,  "end", filehandle, onlyprintanswers, verbose, reallyverbose )
        x = x + xincrement
    return 1

def drawNum(x,y,number,color, align, fontsize, anchor, filehandle, onlyprintanswers,verbose, reallyverbose):

    align=float(align)
    if(onlyprintanswers):
        return 1

# Inkscape doesn't read the 'dominant-baseline="central" ' parameter for text.
# This creates a problem because I can't do raw y-offsets without knowing
# the size of the font. FIXME
 
    if (anchor==""):
        anchor="end"

    x=float(x) + float(align)  # -3 for numbers to the side; 0 for within-the-circle numbers
    
    if (anchor=="end"):
        if (fontsize==9):
            classname='class="sizenineend" '
        elif (fontsize==10):
            classname='class="sizetenend" '
        else:
            pass
        if reallyverbose:
            print 'Anchor is "end" and fontsize is "' + str(fontsize) + '"'
    elif(anchor=="middle"):
        if (fontsize==9):
            classname='class="sizeninemiddle" '
        if reallyverbose:
            print 'Anchor is "middle" and fontsize is "' + str(fontsize) + '"'
    else:
        classname=str('fill="' + color +  \
        '" font-family="Arial" font-size="' + str(fontsize) + \
        '" text-anchor="end"')

    text = str('<text ' + classname + '  x="' + str(x) + 'mm" y="' + \
    str(y) + 'mm"><tspan dy="3">' + str(number) + '</tspan></text>\n')

    filehandle.write(str(text))
    return 1

def getAnswers(filename,verbose):
    
    if(os.path.isfile(filename)):
        print("Found file " + filename + " -- continuing.")
    else: 
        print("Unable to find input file " + filename + " -- check to see it is in the same directory as this program, or create it." )
        sys.exit()

    rt = open(filename, 'r')
    rs = rt.read()
    rs=re.sub('\n$','',rs)
    answerstrings = rs.split('\n')
#    if verbose:
#        print(str(answerstrings))

    answerints = map( int, answerstrings )
    return answerints

def printBlueLines(**params ):
    verbose=params['verbose']
    filehandle=params['filehandle']
    onlyprintanswers=params['onlyprintanswers']

    params['hexcolor'] = re.sub('"', '', params['hexcolor'])
    hexcolor=params['hexcolor']

    if(params['onlyprintanswers'] == 1):
        if (verbose ==1):
            print "Since 'onlyprintanswers' is 1, there's no ' + \
            'need to print anything from this function."
        return 1
    else:
# print the parbox in the upper right:
        filehandle.write('<rect x="130.0mm" y="12mm" width="144mm" height="12.5mm" rx="0.1mm" ry="0.1mm"\nstroke="#5050b4" stroke-width="0.2mm" fill="none" />\n')

# print the heavy vertical divider:
    filehandle.write(str('<line x1="127.5mm" y1="12mm" x2="127.5mm" y2="207mm" style="stroke:rgb(80,80,180);stroke-width:3.5mm" />\n'))

# print the thin horizontal divider:
    filehandle.write(str('<line x1="129.2mm" y1="118mm" x2="275mm" y2="118mm" style="stroke:rgb(80,80,180); stroke-width=0.1mm"/>\n'))

    text1params = {'text1': "GENERAL PURPOSE - PYTHON - ANSWER SHEET",\
    'x':140 , \
    'y':17.5, \
    'font':"Arial", \
    'fontsize':18, \
    'hexcolor':hexcolor, \
    'onlyprintanswers':onlyprintanswers,\
    'verbose':verbose, \
    'filehandle':filehandle \
    }
    
#    if verbose:
#        print("\n*\ttext1params is a: " + str(type(text1params)))
#        print("text1params is : %s " % (text1params) )

    writeText(**text1params)

    text1params={'text1': "SEE IMPORTANT MARKING INSTRUCTIONS ON SIDE 2", \
    'x':153 , \
    'y':22.5, \
    'font':"Arial", \
    'fontsize':13, \
    'filehandle':filehandle, \
    'onlyprintanswers':params['onlyprintanswers'],\
    'hexcolor':hexcolor, \
    'verbose':params['verbose'], \
    'filehandle':params['filehandle'] \
    }
    
    writeText(**text1params ) 

    return 1

def get_selected_values(d, *args):
    return [d[arg] for arg in args]

def writeStyledText(xpos,ypos,classname,text,filehandle,verbose):
    '''write arbitrary text with a class format, at arbitrary coordinates. '''
# typically classname would be "regular" but of course there can be exceptions 
    line=str('<text x="' + str(xpos) + 'mm" y="' + str(ypos) + 'mm" class="' + \
    str(classname) + '">' + \
    str(text) + "</text>\n")
    filehandle.write(line)
    return 1

def writeText(**tp):
    if (tp['onlyprintanswers'] == 1) :
        return 1

    if (tp['verbose'] == 1 ):
        print ("\n*\ttextparams (tp) is: %s" % (tp) ) 

    filehandle=tp['filehandle']

    line = str('<text x="%(x)smm" y="%(y)smm" ' \
    'fill="%(hexcolor)s" font-family="%(font)s" font-size="%(fontsize)s" ' \
    'text-anchor="start" dominant-baseline="auto" >%(text1)s</text>\n' % tp )
    
    filehandle.write(line)
    return 1

class TextWriter(object):
    TEXT_FORMAT = '<text x="%(x)smm" y="%(y)smm" fill="%(color)s" ' \
                  'font-family="%(font)s" font-size="%(fontsize)s" ' \
                  'text-anchor="start" dominant-baseline="auto">' \
                  '%(text)s</text>\n'

    def __init__(self, filehandle, onlyprintanswers=False):
        self.f = filehandle
        self.onlyprintanswers = onlyprintanswers

    def __del__(self):
        self.f.close()

    def writeText(self, text, **kwargs):
        if self.onlyprintanswers:
            return

        kwargs['text'] = text
        kwargs.setdefault('x', '0')
        kwargs.setdefault('y', '0')
        kwargs.setdefault('color', 'black')
        kwargs.setdefault('font', 'serif')
        kwargs.setdefault('fontsize', 12)

        self.f.write(self.TEXT_FORMAT % kwargs)

# writer = TextWriter(filehandle=open('test.xml', 'w'))
# writer.writeText('hello world', x=100, y=100, color='blue')

def which(program): 
# Thanks to Jay (http://stackoverflow.com/users/20840/jay) for this.
# http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def checkForInkscape(inkscapedict, params):
    verbose=params['verbose']
    reallyverbose=params['reallyverbose']
    for key, value in inkscapedict.iteritems():
        if reallyverbose:
            print(key + '\t' + str(value[0] ))

        if (which(value[0])):
            inkscape=1
            if verbose:
                print(str(value[1]))
            return str(value[0])

    return False

# EOF
