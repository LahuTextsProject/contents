import re
import fileinput

footnoteson = False
lineArray = []
footHash = {}

footnote_number_pattern = re.compile(r'^\[(\d+)\] *(.*)')

for line in fileinput.input():
    line = line.strip()
    line = line.replace('\texttt{"}', '"')
    line = re.sub(r'\@(.*?)\@', '_{\1}', line);
    line = line.replace('\Huge{}', '');
    line = line.replace('\huge{}', '');
    if 'vspace' in line: continue
    if 'parindent' in line: continue
    if 'baselineskip' in line: continue
    if 'Footnote' in line: footnoteson = True
    if re.match(r'^\[\d+\]',line): footnoteson = True
    if footnoteson:
        textnumbermatch = footnote_number_pattern.search(line)
        if textnumbermatch:
            footnote_number = textnumbermatch.group(1)
            rest_of_line = textnumbermatch.group(2)
            footHash[footnote_number] = rest_of_line
    else:
        lineArray.append(line)
for line in lineArray:
    line = re.sub(r'([\d+])\.', '\.\1', line)
    for fn in footHash:
        line = line.replace('[%s]' % fn, ("\\footnote{%s}" % footHash[fn]))
    print line
