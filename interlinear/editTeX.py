import re
import fileinput
import csv

footnoteson = False
lineArray = []
footHash = {}

footnote_number_pattern = re.compile(r'^\[(\d+)\] *(.*)')

def makeLahuWords():
    lahuWords = []
    with open('triples.csv', 'rb') as triples:
        reader = csv.reader(triples, delimiter = '\t')
        for row in reader:
            lahuWords.append(row[1])
    return lahuWords

lahuWords = makeLahuWords()

def fixLine(line):
    line = line.strip()
    line = re.sub(r'\\texttt\{"\}', r'``', line);
    line = re.sub(r'\\texttt\{\'\}', r'`', line);
    line = re.sub(r'\\texttt\{(.*?)\}', r'\1', line);
    line = re.sub(r'([A-Z])\@(.*?)\@', r'$\1_\2$', line);
    line = re.sub(r'\@([a-z])\@(.*?)', r'$_{\1}\2$', line);
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

englishLahuOverlap = ['to', 'a', 'the', 'The']
    
def boldLahu(footnoteObj):
    # bold the Lahu in a footnote - we punt when a word could be
    # either English or Lahu
    # TODO: Do we want to bold the colon or not?
    footnoteContents = footnoteObj.group(0)
    words = re.split(r' ', footnoteContents)
    newstring = ''
    for word in words:
        wordstrip = word.replace(':', '')
        if (wordstrip in lahuWords) and (wordstrip not in englishLahuOverlap):
            newstring += ('\\textbf{%s} ' % word)
        else:
            newstring += word + ' '
    return newstring[:-1]

for line in lineArray:
    # move footnote mark outside period: xxx xx[99]. ->  xxx xx.[99]
    line = re.sub(r'(\[\d+\])\.', r'.\1', line)
    for fn in footHash:
        line = line.replace('[%s]' % fn, ("\\footnote{%s}" % footHash[fn]))
    line = re.sub(r'(?<=\\footnote{)[^}]*}', boldLahu, line)
    print line
