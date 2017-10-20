grep "gls" lahutexts.xml | grep -v segnum | perl -pe 's/<item type="gls" lang="en">(.*)<\/item>/\1/' | sort | uniq -c | sort -rn | perl -pe 's/^ *(\d+) /\1\t/' > glosses.csv
grep "txt" lahutexts.xml | grep -v segnum | perl -pe 's/^.*?<word><item type=\"txt\" lang=\"en\">(.*)<\/item>.*$/\1/' | sort | uniq -c | sort -rn | perl -pe 's/^ *(\d+) /\1\t/' > forms.csv

# TODO Exclude Black | Lahu | translation from file somehow
perl -ne 'next if /segnum/;s/\r//; print "\n" if /<\/morph>/; chomp; if (/(txt|gls|msa)/) {s/^.*?lang=\"(?:en|lhu)\">(.*)<\/item>.*$/\1/;print ; print "\t";}' lahutexts.xml | grep -v segnum > elements.csv
perl -ne 'next if /segnum/;s/\r//; print "\n" if /<\/morph>/; chomp; if (/msa/) {s/^.*?lang=\"(?:en|lhu)\">(.*)<\/item>.*$/\1/;print ; print "\t";}' lahutexts.xml | grep -v segnum | uniq -c > abbreviations.csv
sort elements.csv | uniq -c | sort -rn | perl -pe 's/^ *(\d+) /\1\t/' > triples.csv
