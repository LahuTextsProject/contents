# -*- coding: utf-8 -*-

import re
import fileinput
import csv
import unicodedata

from string import punctuation
from formclass import parse_form_class_file

form_class_info = parse_form_class_file('annotated_abbreviations.tsv')

def normalize_unicode(word):
    return unicodedata.normalize('NFC', unicode(word, 'utf-8'))

def makeLahuWords():
    words = set()
    with open('pruned_elements.csv', 'rb') as triples:
        reader = csv.reader(triples, delimiter='\t')
        for row in reader:
            if row and row[0]:
                words.add(normalize_unicode(row[0]))
    return words

lahuWords = makeLahuWords()
# these are either morphemes that appear in Lahu,
# or otherwise words that can't be reanalyzed into
# smaller pieces and not in the dictionary
for morpheme in ['ɔ̀',
                 'cɛ́ʔ',  # Transcribed Burmese morpheme
                 'nîʔkho',
                 'lɔ̂kì',
                 'rê',
                 'šo',  # Iron
                 'tàʔ'
]:
    lahuWords.add(normalize_unicode(morpheme))

def pretty_form_class(line):
    newstring = ''
    for word in line.split():
        wordstrip = word.strip(punctuation)
        if wordstrip in form_class_info:
            pretty = str(form_class_info[wordstrip][1])
            newstring += word.replace(wordstrip, pretty)
        else:
            newstring += word
        newstring += ' '
    return newstring[:-1]

def fixLine(line):
    line = line.strip()
    # sub in allofam symbol, as Charis SIL doesn't support it
    line = line.replace('\xe2\xaa\xa4', r'$\glj$')
    line = line.replace(r'\\texttt\{"\}', r'"')
    line = line.replace(r'\\texttt\{\'\}', r"'")
    line = re.sub(r'"(.*?)"', r"``\1''", line)
    line = re.sub(r'\\texttt\{(.*?)\}', r'\1', line)
    line = re.sub(r'([A-Z])\@(.*?)\@', r'$\1_\2$', line)
    line = re.sub(r'\@([a-z])\@(.*?)', r'$_{\1}\2$', line)
    # replace upper case acute accent a with lower case
    line = line.replace('\xc3\x81', '\xc3\xa1')
    line = line.replace('\Huge{}', '')
    line = line.replace('\huge{}', '')
    # make form class abbreviations look pretty
    line = pretty_form_class(line)

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
    for (i, word) in enumerate(words):
        wordstrip = word.strip(punctuation)
        if isLahuWord(wordstrip) or \
           (wordstrip == 'a' \
            and isLahuWord(words[i - 1]) \
            and isLahuWord(words[i + 1])):
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
seenfootnotes = set([])
footnote = ''
for line in inputLines:

    if re.match(r'^\[\s*\d+\s*\]',line):

        addnote(footnote,footHash)
        footnote = line
        
    else:
        footnote += ' ' + line

addnote(footnote,footHash)

# an alternative algorithm would be to scan the line and extract the
# footnote number, and then do a lookup. This is a good approach
# because we can detect uses without definitions
def fixup_footnotes(line):
    for number, footnote_text in footHash.iteritems():
        footnote = '\\footnote{%s}' % footnote_text
        if '[%s]' % number in line:
            seenfootnotes.add(number)
        line = line.replace(' [%s]' % number, footnote)
        line = line.replace('[%s]' % number, footnote)
    return line

# skip the first non-empty line, which is the title
# we emit the real title from the catalog file
for (i, line) in enumerate(lineArray):
    if not line.strip():
        continue
    else:
        text_start = i + 1
        break

print r'\setcounter{footnote}{0}'
line_number_pattern = re.compile(r'^(\d+[A-Za-z]?)(\.|\:)?\s*')
for (prologue, line) in enumerate(lineArray[text_start:]):
    if line_number_pattern.match(line):
        break
    elif '[Tape ' in line:
        continue
    elif '[TAPE ' in line:
        continue
    else:
        print fixup_footnotes(line)

dialogue_start = prologue + text_start

## dialogue_pattern_1 = re.compile(r'^([^:]{1,20}):')
## dialogue_pattern_2 = re.compile(r'^\(([^\)]{1,20})\)')
for line in lineArray[dialogue_start:]:
    # normalize line numbering
    line = line_number_pattern.sub(r'\1. ', line)
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
    line = re.sub(r'\s?(\[\d+\])\.', r'.\1', line)
    print fixup_footnotes(line)

# assertions
for key in footHash:
    if key not in seenfootnotes:
        raise ValueError("Footnote %s defined but never used" % key)
