# get the Lahu glosses updated
echo Analyzing Lahu lexicon
./analyze.sh

rm -rf ../t2
mkdir ../t2
cp ../rtfs/*.rtf ../t2
for f in `ls ../t2/*.rtf`
do
    rtf2latex2e -nf $f
done
for f in `ls ../t2/*.tex`
do
    r=$(basename "$f")
    echo "editing $r"
    grep -v 'newpage' $f | python2 editTeX.py > ../transTeX/$r
    #rm $f
done
