# -*- coding: utf-8 -*-

import re
import fileinput
import csv
import unicodedata

from string import punctuation

def normalize_unicode(word):
    return unicodedata.normalize('NFC', unicode(word, 'utf-8'))

def makeLahuWords():
    words = set()
    with open('elements.csv', 'rb') as triples:
        reader = csv.reader(triples, delimiter = '\t')
        for row in reader:
            words.add(normalize_unicode(row[0]))
    return words

lahuWords = makeLahuWords()
# these are either morphemes that appear in Lahu,
# or otherwise words that can't be reanalyzed into
# smaller pieces and not in the dictionary
for morpheme in ['ɔ̀',
                 'cɛ́ʔ', # Transcribed Burmese morpheme
                 'Kɔ́lɔ',
                 'nîʔkho',
                 'lɔ̂kì',
                 'rê',
                 'šo', # Iron
                 'tàʔ'
]:
    lahuWords.add(normalize_unicode(morpheme))

def fixLine(line):
    line = line.strip()
    line = line.replace(r'\\texttt\{"\}', r'"')
    line = line.replace(r'\\texttt\{\'\}', r"'")
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
                          'To', 'I', 'Paul', 'Pastor', 'Teacher',
                          'Tcalo', 'selection', 're-recorded', 'Another'])

def isLahuWord(word):
    # detect whether a word (sans formatting but with case) is Lahu
    # some heuristics:
    # a word is in the overlap? no
    # a morpheme is in the gloss? yes
    if word in englishLahuOverlap:
        return False
    # u+a78a is the double hypen morpheme separater
    word = normalize_unicode(word)
    if word in lahuWords:
        return True
    for morpheme in re.split(u'-|\ua78a', word):
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

footnote_number_pattern = re.compile(r'^\[(\d+)\] *(.*)')
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

lineArray = []
footnoteson = False
line_continuation = False
# Collect all non footnote lines from input
for pointer, line in enumerate(inputLines):
    if 'Footnote' in line: break
    # match the footnote only when the line preceding it is not a newline
    # as that means that this is the continuation of a sentence
    if re.match(r'^\[\d+\]', line):
        if line_continuation == True:
            None
        else:
            break
    if line.isspace():
        line_continuation = False
    else:
        line_continuation = True
    lineArray.append(line)

inputLines = inputLines[pointer:]

# process footnotes
footHash = {}
footnote = ''
for line in inputLines:

    if re.match(r'^\[\d+\]',line):

        addnote(footnote,footHash)
        footnote = line
        
    else:
        footnote += ' ' + line

addnote(footnote,footHash)

# skip the first non-empty line, which is the title
for (i, line) in enumerate(lineArray):
    if not line.strip():
        continue
    else:
        text_start = i + 1
        break

print r'\setcounter{footnote}{0}'
line_number_pattern = re.compile(r'^\d+[A-Za-z]?(\.|\:)?\s*')
for (dialogue_start, line) in enumerate(lineArray[text_start:]):
    if line_number_pattern.match(line):
        break
    else:
        print line

## dialogue_pattern_1 = re.compile(r'^([^:]{1,20}):')
## dialogue_pattern_2 = re.compile(r'^\(([^\)]{1,20})\)')
print r'\begin{linenumbers*}'
for line in lineArray[dialogue_start + text_start:]:
    # strip RTF line numbers
    line = line_number_pattern.sub(r'', line)
    # normalize speaker names
    line = re.sub(r'(Cà-bo|Càbo|CB|Pastor|Teacher)\:', 'T:', line)
    line = re.sub(r'(T-y|Thû-Yì|Thû-yì|Thúyì|TY)\:', 'Ty:', line)
    line = line.replace('Headman:', 'H:')
    line = re.sub(r'(Paul|Càlɔ|Cà-lɔ|Cà-lɔ̂|CL|Tcalo)\:', 'P:', line)
    # format stage directions
    line = re.sub(r'<([^\>]+)>', r'\direct{\1}', line)
    # normalize whitespace in footnote mark
    line = re.sub(r'\[ *(\d+) *\]', r'[\1]', line)
    # move footnote mark outside period: xxx xx[99]. ->  xxx xx.[99]
    line = re.sub(r'(\[\d+\])\.', r'.\1', line)
    for fn in footHash:
        line = line.replace(' [%s]' % fn, ("\\footnote{%s}" % footHash[fn]))
        line = line.replace('[%s]' % fn, ("\\footnote{%s}" % footHash[fn]))
    print line
print r'\end{linenumbers*}'
