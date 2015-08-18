for f in `ls ../rtfs/*.rtf`
do
  rtf2latex2e $f
done
for f in `ls ../rtfs/*.tex`
do
  r=$(basename "$f")
  sed -n '/begin/,$p' $f | tail -n +2 | sed -n '/end{document}/q;p' | grep -v 'newpage' > ../transTeX/$r
  rm $f
done
