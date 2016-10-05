# svgscantron
A LaTeX multiple-choice test template, plus python-based conversion into a pre-formatted Scantron ('bubble sheet') answer svg/png.

This package is a collection of a customized LaTeX preamble and a python script that is run within the LaTeX compile 
(if you have enabled shell access for your LaTeX editor). 
The example test (`exampletest.tex`) and survey (`survey.tex`) show you most of the functionality of the script. 

:exclamation: The most important function is whether or not the `"keytrue"` variable is enabled or not.

```[Latex]
\keyfalse
% Uncommenting \keytrue would set the "key" variable to TRUE:
% \keytrue
```

If the `\keytrue` is enabled, then the test will compile with all of the answers printed in bold face, with the correct multiple choice answer letter displayed in bright green. 

If the `\keytrue` is commented out (that is, only `\keyfalse` is enabled) then the test will print as a student would see it. 

With some additional work, the python script will print a scantron answer sheet for you. It's not perfect, but it works. 
There's a default for an 'official' Scantron 4521 form, but it's possible to add other formats. 
I've added one for a knockoff 4521 form. It's close, but not really -- definitely not close enough for the original format to work.
```[latex]
% formdefs is the specific formatting information required for the 
% Scantron form you wish to use. 
\newcommand{\formdefs}{old4521.txt}
```
Beyond that, the sample test is pretty easy to follow. If you find it useful, let me know.

If you have problems with a specific printer, let me know but it's unlikely I can fix the error from this end. 
The printer needs to be pretty accurate, and junk printers just won't have the precision needed to do a repeatably good job.

To make a "blue" scantron sheet, the python script `makesvg.py` can do that 
(or just make a blank set of dots, suitable for printing on the appropriate form).

```[shell]
python makesvg.py -f BlueScantronAnswers -v -a answerlist.txt  -l "Your text can go here." -i old4521.txt 
```

:rocket: Jesse Hamner, 2015--2016.
