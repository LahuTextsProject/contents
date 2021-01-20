if [[ `pwd` != */interlinear ]]; then
  echo "you must cd to directory interlinear before invoking this script"
  exit
fi
texfile="WindowsForgottenWorld"
xml_file=$1
mkdir -p ../t2
echo
echo "=============================================================================="
echo Starting run `date`
case $2 in baptist|chinese|matisovian)
      which_part="$2"
      echo "Will generate the '$which_part' transcription version." ;;
    *)
      echo 'Second argument must be one of baptist|chinese|matisovian'
      exit 1 ;;
esac
echo Making symbolic link lahutexts.xml. source is: $1
cp $xml_file lahutexts.xml
echo Converting RTFs to LaTeX
./texRTFs.sh
echo Making music scores
if [[ `uname` == "Darwin" ]]
then
   # for jb's mac:
   /Applications/LilyPond.app/Contents/Resources/bin/lilypond --ps Lahu_tune.ly
else
   # for charles' linux:
   lilypond --ps Lahu_tune.ly
fi
echo Performing fixups
./fixups.sh
#
# cd to the tex directory for heavy lifting, copy files as necessary from elsewhere
#
cd tex
rm -r *
cp ../*.eps .
cp ../$xml_file .
cp ../*.tex .
cp ../../transTeX/*.tex .
cp ../*.bib .
echo Generating LaTeX file "${texfile}.tex", timestamp: `date`

shift
echo "python ../generateLaTeX.py $xml_file ../lahucatalog.tsv ../annotated_abbreviations.tsv ../triples.csv $which_part"
/usr/bin/python ../generateLaTeX.py $xml_file ../lahucatalog.tsv ../annotated_abbreviations.tsv ../triples.csv "$which_part"

sed -e '/% insert includes here/r./includes.tex' lahuTemplate.tex > ${texfile}.tex

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
