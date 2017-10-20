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
cd tex
rm -r *
cp ../$1 .
cp ../*.tex .
cp ../../transTeX/*.tex .
echo Generating LaTeX file "${texfile}.tex", timestamp: `date`
python2 ../generateLaTeX.py $1 ../lahucatalog.tsv

# python ../combiner.py ../lahutextstoc.txt
sed -e '/% insert includes here/r./includes.tex' lahuTemplate.tex > ${texfile}.tex
#
echo Compiling LaTeX file "${texfile}.tex", step 1 of 3, timestamp: `date`
xelatex -interaction nonstopmode ${texfile} > ${texfile}.stdout.log
echo Compiling LaTeX file "${texfile}.tex", step 2 of 3, timestamp: `date`
xelatex -interaction nonstopmode ${texfile} >> ${texfile}.stdout.log
echo Compiling LaTeX file "${texfile}.tex", step 3 of 3, timestamp: `date`
xelatex -interaction nonstopmode ${texfile} >> ${texfile}.stdout.log
echo Done. `date`
echo Output is tex/${texfile}.tex, logs are in ${texfile}.stdout.log
echo "=============================================================================="
