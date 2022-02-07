# Lahu Texts Project
All code and content for the Lahu Texts Project

_Caveat lector: the code and texts here are *incomplete* and *in progress*_

While the material here is being made avaiable under the Apache License, we
would appreciate it if users and viewers treat the material with the 
discretion it deserves and allow us to work quietly on it for the next
few months until it is ready for publication.

Comments and suggestions are of course most welcome!

# Prerequisites
* Python 3 (current using 3.9), we _think_ it requires no other packages...
* Two fonts (SIL Charis and Babelstone Han)
* A suitable XeLaTeX installation (including a number of Math and other packages). Currently using MacTeX Live and Ubuntu version.
* (It used to require Lilypond to generate an EPS graphic of a music score but now we have frozen that part of the pipeline)

## LaTeX packages
* `glossaries`
* `covington`, for IGT formatting
probably some math packages as well..

# Building
To build the pdf, run the shell script from within the `interlinear` directory. At the moment, it takes 3-5 minutes 
on a MacBook Pro M1, so we like to `nohup` it
and run it in the background. This makes it possible to monitor progress by `tail`ing `nohup.out`.
```
cd interlinear
rm nohup.out ; nohup ./makeLahuTexts.sh lahuinterlinear.xml matisovian &
```

NB: it used to be possible to build with baptist and chinese transcriptions, but at the moment that is disabled.

## Python packages
`unicodecsv`, for Python 2.7 version, available in pip
