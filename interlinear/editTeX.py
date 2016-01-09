import re
import fileinput

footnoteson = False
lineArray = []
footHash = {}

footnote_number_pattern = re.compile(r'^\[(\d+)\] *(.*)')

def fixLine(line):
    
    line = line.strip()
    line = re.sub(r'\\texttt\{(.*?)\}', r'\1', line);
    line = re.sub(r'\@(.*?)\@', '_{\1}', line);
    line = line.replace('\Huge{}', '');
    line = line.replace('\huge{}', '');

    return line

def test4skip(line):
    
    if 'vspace' in line: return True
    if 'parindent' in line: return True
    if 'baselineskip' in line: return True

    return False

def addnote(footnote,footHash):
    
    textnumbermatch = footnote_number_pattern.search(footnote)
    if textnumbermatch:
        footnote_number = textnumbermatch.group(1)
        rest_of_line = textnumbermatch.group(2)
        footHash[footnote_number] = rest_of_line.strip()

inputLines = []
for line in fileinput.input():
    line = fixLine(line)
    if test4skip(line): continue
    inputLines.append(line.strip())

for pointer, line in enumerate(inputLines):
    if 'Footnote' in line: footnoteson = True
    if re.match(r'^\[\d+\]',line): footnoteson = True
    if footnoteson:
        break
    lineArray.append(line)

inputLines = inputLines[pointer:]

# process footnotes
footnote = ''
for line in inputLines:

    if re.match(r'^\[\d+\]',line):

        addnote(footnote,footHash)
        footnote = line
        
    else:
        footnote += ' ' + line

addnote(footnote,footHash)
    
for line in lineArray:
    # move footnote mark outside period: xxx xx[99]. ->  xxx xx.[99]
    line = re.sub(r'(\[\d+\])\.', r'\.\1', line)
    #line = re.sub(r'([\d+])', r'\1', line)
    for fn in footHash:
        line = line.replace('[%s]' % fn, ("\\footnote{%s}" % footHash[fn]))
    print line
