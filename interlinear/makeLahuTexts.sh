if [[ `pwd` != */interlinear ]]; then
  echo "you must cd to directory interlinear before invoking this script"
  exit
fi
texfile="WindowsForgottenWorld"
xml_file=$1
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

# we now skip this part ... use the generate .eps file
#echo Making music scores
#if [[ `uname` == "Darwin" ]]
#then
#   # for jb's mac:
#   /Applications/LilyPond.app/Contents/Resources/bin/lilypond --ps Lahu_tune.ly
#else
#   # for charles' linux:
#   lilypond --ps Lahu_tune.ly
#fi
# echo Performing fixups
# ./fixups.sh
#
# cd to the tex directory for heavy lifting, copy files as necessary from elsewhere

# the tex directory is the 'working directory' all text files, go in there
rm -rf tex
mkdir tex
cd tex

cp ../*.eps .
cp ../*.png .
cp ../$xml_file lahutexts.xml
cp ../*.tex .
cp ../../transTeX/*.tex .
cp ../*.bib .
cp ../lahucatalog.tsv .
cp ../annotated_abbreviations.tsv .

echo Generating LaTeX file "${texfile}.tex", timestamp: `date`

shift

# echo Preparing intermediate files
../PrepareFiles.sh

echo "python3 ../generateLaTeX.py lahutexts.xml lahucatalog.tsv annotated_abbreviations.tsv triples.csv $which_part"
python3 ../generateLaTeX.py lahutexts.xml lahucatalog.tsv annotated_abbreviations.tsv triples.csv "$which_part"

sed -e '/% insert includes here/r./includes.tex' lahuTemplate.tex > ${texfile}.tex

echo Compiling LaTeX file "${texfile}.tex", step 1 of 3, timestamp: `date`
xelatex -interaction nonstopmode ${texfile} > ${texfile}.stdout1.log
echo Generating glossaries
makeglossaries ${texfile} > ${texfile}.glossaries.stdout.log
echo Generating bibliography
bibtex ${texfile} > ${texfile}.bibtex.stdout.log
echo Compiling LaTeX file "${texfile}.tex", step 2 of 3, timestamp: `date`
xelatex -interaction nonstopmode ${texfile} > ${texfile}.stdout2.log
echo Compiling LaTeX file "${texfile}.tex", step 3 of 3, timestamp: `date`
xelatex -interaction nonstopmode ${texfile} > ${texfile}.stdout3.log
echo Done. `date`
echo Output is tex/${texfile}.tex, logs are in the 3 ${texfile}.stdoutN.log files
echo "=============================================================================="
