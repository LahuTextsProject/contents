rm ../t2/*
cp ../rtfs/*.rtf ../t2
for f in `ls ../t2/*.rtf`
do
  rtf2latex2e $f
done
for f in `ls ../t2/*.tex`
do
  r=$(basename "$f")
  sed -n '/begin/,$p' $f | tail -n +2 | sed -n '/end{document}/q;p' | grep -v 'newpage' | python editTex.py > ../transTeX/$r
  #rm $f
done
