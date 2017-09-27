import re
import fileinput
import csv
import string

footnoteson = False
lineArray = []
footHash = {}

footnote_number_pattern = re.compile(r'^\[(\d+)\] *(.*)')

def makeLahuWords():
    lahuWords = []
    with open('elements.csv', 'rb') as triples:
        reader = csv.reader(triples, delimiter = '\t')
        for row in reader:
            lahuWords.append(row[0])
    return lahuWords

lahuWords = makeLahuWords()

def fixLine(line):
    line = line.strip()
    line = re.sub(r'\\texttt\{"\}', r'``', line)
    line = re.sub(r'\\texttt\{\'\}', r'`', line)
    line = re.sub(r'\\texttt\{(.*?)\}', r'\1', line)
    line = re.sub(r'([A-Z])\@(.*?)\@', r'$\1_\2$', line)
    line = re.sub(r'\@([a-z])\@(.*?)', r'$_{\1}\2$', line)
    # replace upper case acute accent a with lower case
    line = line.replace('\xc3\x81', '\xc3\xa1')
    line = line.replace('\Huge{}', '')
    line = line.replace('\huge{}', '')

    return line

def test4skip(line):
    
    if 'vspace' in line: return True
    if 'parindent' in line: return True
    if 'baselineskip' in line: return True

    return False

englishLahuOverlap = ['to', 'a', 'the', 'The', 'they', 'Black', 'some', 'do', 'go']

punctuation_sans_hyphen = string.punctuation.replace('-', '')

def stripItalics(line):
    line = re.sub(r'\\textit\{([^}]*)\}', r'\1', line)
    line = re.sub(r'\\emph\{([^}]*)\}', r'\1', line)
    return line

def boldLahu(line):
    # bold the Lahu in a line - we punt when a word could be
    # either English or Lahu
    # TODO: Do we want to bold the punctuation or not? probably not
    # some heuristics: if a word is in the gloss, then bold
    # if a hyphenated component is in the gloss, then bold
    # if a word is in the overlap, don't bold
    # if a hyphenated component is in the overlap, do bold
    words = line.split()
    newstring = ''
    for word in words:
        lahuMorpheme = False
        wordstrip = word.translate(None, punctuation_sans_hyphen).lower()
        for morpheme in wordstrip.split('-'):
            if morpheme in lahuWords:
                lahuMorpheme = True
        if (lahuMorpheme is True) and (wordstrip not in englishLahuOverlap):
            newstring += ('\\textbf{%s} ' % word)
        else:
            newstring += word + ' '
    return newstring[:-1]

def addnote(footnote,footHash):
    
    textnumbermatch = footnote_number_pattern.search(footnote)
    if textnumbermatch:
        footnote_number = textnumbermatch.group(1)
        rest_of_line = textnumbermatch.group(2).strip()
        # process footnote contents
        footnote_contents = boldLahu(stripItalics(rest_of_line))
        footHash[footnote_number] = footnote_contents

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
    line = re.sub(r'(\[\d+\])\.', r'.\1', line)
    for fn in footHash:
        line = line.replace('[%s]' % fn, ("\\footnote{%s}" % footHash[fn]))
    print line
