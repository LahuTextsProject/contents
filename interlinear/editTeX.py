import re
import fileinput
import csv
import unicodedata

from string import punctuation

footnoteson = False
lineArray = []
footHash = {}

footnote_number_pattern = re.compile(r'^\[(\d+)\] *(.*)')

def makeLahuWords():
    lahuWords = set()
    with open('elements.csv', 'rb') as triples:
        reader = csv.reader(triples, delimiter = '\t')
        for row in reader:
            lahuWords.add(unicodedata.normalize('NFC', unicode(row[0], 'utf-8')))
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

englishLahuOverlap = set(['to', 'a', 'the', 'The', 'They', 'they',
                          'Black', 'some', 'do', 'go', 'A', 'much',
                          'To'])

def isLahuWord(word):
    # detect whether a word (sans formatting but with case) is Lahu
    # some heuristics:
    # a word is in the overlap? no
    # a morpheme is in the gloss? yes
    if word in englishLahuOverlap:
        return False
    # \xea is the double hyphen morpheme separater
    for morpheme in re.split('-|\xea', unicodedata.normalize('NFC', unicode(word.lower(), 'utf-8'))):
        if morpheme in lahuWords:
            return True
    return False

def containsLahu(string):
    for word in string.split():
        if isLahuWord(word.strip(punctuation)):
            return True
    return False

def stripLahuFormatting(string):
    def subfun(match):
        contents = match.group(1)
        # we strip 3 characters or less because some Lahu
        # fragments are only partially formatted
        if (containsLahu(match.group(1))) or (len(contents.decode('utf-8')) <= 3):
            return match.group(1)
        else:
            return match.group(0)
    return re.sub(r'\\(?:textit|emph|textbf)\{([^}]*)\}', subfun, string)

def boldLahu(string):
    # bold all Lahu words in a string
    # preserve all punctuation elements
    words = string.split()
    newstring = ''
    for word in words:
        wordstrip = word.strip(punctuation)
        if isLahuWord(wordstrip):
            newstring += word.replace(wordstrip, ('\\textbf{%s}' % wordstrip))
        else:
            newstring += word
        newstring += ' '
    return newstring[:-1]

def addnote(footnote,footHash):
    textnumbermatch = footnote_number_pattern.search(footnote)
    if textnumbermatch:
        footnote_number = textnumbermatch.group(1)
        rest_of_line = textnumbermatch.group(2).strip()
        # process footnote contents
        footnote_contents = boldLahu(stripLahuFormatting(rest_of_line))
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
    # normalize whitespace in footnote mark
    line = re.sub(r'\[ *(\d+) *\]', r'[\1]', line)
    # move footnote mark outside period: xxx xx[99]. ->  xxx xx.[99]
    line = re.sub(r'(\[\d+\])\.', r'.\1', line)
    for fn in footHash:
        line = line.replace('[%s]' % fn, ("\\footnote{%s}" % footHash[fn]))
    print line
