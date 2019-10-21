if [[ `pwd` != */interlinear ]]; then
  echo "you must cd to directory interlinear before invoking this script"
  exit
fi
#
# cd to the tex directory for all the work, copy files as necessary
#
texfile="WindowsForgottenWorld"
echo
echo "=============================================================================="
echo Starting run `date`
echo Making symbolic link lahutexts.xml
ln -sf $1 lahutexts.xml
echo Converting RTFs to LaTeX
./texRTFs.sh
echo Making music scores
# for charles' linux:
lilypond --ps Lahu_tune.ly
# for jb's mac:
# /Applications/LilyPond.app/Contents/Resources/bin/lilypond --ps Lahu_tune.ly
echo Performing fixups
./fixups.sh
cd tex
rm -r *
cp ../*.eps .
cp ../$1 .
cp ../*.tex .
cp ../../transTeX/*.tex .
cp ../*.bib .
echo Generating LaTeX file "${texfile}.tex", timestamp: `date`
xml_file=$1
shift
python2 ../generateLaTeX.py $xml_file ../lahucatalog.tsv ../annotated_abbreviations.tsv ../triples.csv "$@"

# python ../combiner.py ../lahutextstoc.txt
sed -e '/% insert includes here/r./includes.tex' lahuTemplate.tex > ${texfile}.tex

# this is commented out as we want both chinese and baptist transcriptions
if [ "$@" ] # assumes both will be added
then
    sed -i -e 's/%\\baptisttableofcontents/\\baptisttableofcontents/' ${texfile}.tex
    sed -i -e 's/%\\chinesetableofcontents/\\chinesetableofcontents/' ${texfile}.tex
fi

echo Compiling LaTeX file "${texfile}.tex", step 1 of 3, timestamp: `date`
xelatex -interaction nonstopmode ${texfile} > ${texfile}.stdout.log
echo Generating glossaries
makeglossaries ${texfile} > ${texfile}.glossaries.stdout.log
echo Generating bibliography
bibtex ${texfile} > ${texfile}.bibtex.stdout.log
echo Compiling LaTeX file "${texfile}.tex", step 2 of 3, timestamp: `date`
xelatex -interaction nonstopmode ${texfile} >> ${texfile}.stdout.log
echo Compiling LaTeX file "${texfile}.tex", step 3 of 3, timestamp: `date`
xelatex -interaction nonstopmode ${texfile} >> ${texfile}.stdout.log
echo Done. `date`
echo Output is tex/${texfile}.tex, logs are in ${texfile}.stdout.log
echo "=============================================================================="
