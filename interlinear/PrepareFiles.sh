# get the Lahu glosses updated
echo Analyzing Lahu lexicon
OUTPUT_DIR="."
grep "gls" lahutexts.xml | grep -v segnum | perl -pe 's/<item type="gls" lang="en">(.*)<\/item>/\1/' | sort | uniq -c | sort -rn | perl -pe 's/^ *(\d+) /\1\t/' > ${OUTPUT_DIR}/glosses.csv
grep "txt" lahutexts.xml | grep -v segnum | perl -pe 's/^.*?<word><item type=\"txt\" lang=\"(?:en|lhu)\">(.*)<\/item>.*$/\1/' | sort | uniq -c | sort -rn | perl -pe 's/^ *(\d+) /\1\t/' > ${OUTPUT_DIR}/forms.csv

perl -ne 'next if /segnum/;s/\r//; print "\n" if /<\/morph>/; chomp; if (/(txt|gls|msa)/) {s/^.*?lang=\"(?:en|lhu)\">(.*)<\/item>.*$/\1/;print ; print "\t";}' lahutexts.xml | grep -v segnum > ${OUTPUT_DIR}/elements.csv
# TODO Exclude Black | Lahu | translation from file somehow
# we only want the last "txt", which represents the Lahu form
cat ${OUTPUT_DIR}/elements.csv | perl -e 'foreach $line (<STDIN>) {my @words = split /\t/, $line; my $i = $#words; if (@words[$i-1]) {print @words[$i-3]; print "\t"; print @words[$i-2]; print "\t"; print @words[$i-1]; print "\n"}}' > ${OUTPUT_DIR}/pruned_elements.csv
perl -ne 'next if /segnum/;s/\r//; print "\n" if /<\/morph>/; chomp; if (/msa/) {s/^.*?lang=\"(?:en|lhu)\">(.*)<\/item>.*$/\1/;print ; print "\t";}' lahutexts.xml | grep -v segnum | sort | uniq > ${OUTPUT_DIR}/abbreviations.csv
sort ${OUTPUT_DIR}/pruned_elements.csv | uniq -c | sort -rn | perl -pe 's/^ *(\d+) /\1\t/' > ${OUTPUT_DIR}/triples.csv
