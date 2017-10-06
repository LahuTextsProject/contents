# get the Lahu glosses updated
echo Analyzing Lahu lexicon
./analyze.sh

rm -rf ../t2
mkdir ../t2
cp ../rtfs/*.rtf ../t2
for f in `ls ../t2/*.rtf`
do
    rtf2latex2e -n $f
done
for f in `ls ../t2/*.tex`
do
    r=$(basename "$f")
    echo "editing $r"
    sed -n '/begin/,$p' $f | tail -n +2 | sed -n '/end{document}/q;p' | grep -v 'newpage' | python2 editTeX.py > ../transTeX/$r
    #rm $f
done
