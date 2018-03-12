# post processing done on specific files
# how to splice in text after string match awk '/master.mplayer.com/ { print; print "new line"; next }1'
# TODO: put music after footnote
cat 66_fixup.tex >> ../transTeX/066_candid_conversation__working_up_to_being_recorded.tex
sed -i -e 's/\\textbf{\/GIVE REF\. WHEN AVAILABLE\/}/section~\\ref{sec:29}/' ../transTeX/133_the_snake_and_the_widow_s_daughters.tex
