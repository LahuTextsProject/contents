#
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import codecs
import sys
import os
import re
import unicodecsv as csv

from Transducer import transduce, baptist, chinese, decompose
from structure import structure, lahu_structure

def parse_catalog_file(filename):
    try:
        catalog_file = open(filename, 'rb')
    except IOError:
        message = 'Expected to be able to read %s, but it was not found or unreadable' % filename
        exit()

    csvfile = csv.reader(catalog_file, delimiter="\t", encoding='utf-8')
    catalog = {}
    # skip header row
    csvfile.next()
    for row, info in enumerate(csvfile):
        # are we using this text?
        if info[17] != 'y':
            continue
        id_number = str(info[7])
        english_title = info[8]
        genre = str(info[11])
        section = str(info[12])
        index = "%s.%02d" % (genre, int('0' + section))
        translation_filename = str(info[15]).replace('.rtf','').replace('.text','').strip()
        catalog[id_number] = [index, translation_filename, genre, float(index), english_title]

    catalog_file.close()
    return catalog

def escape(str):
    str = str.replace('&','\\&')
    str = str.replace('#','\\#')
    str = str.replace('_','\\_')
    #str = str.replace('-','\\-')
    return str

with open(sys.argv[1], 'rt') as f:
    tree = ET.parse(f)

# we'll be reorganizing (reordering) the files as they come in.
# (they don't come in in any useful order)
filestotex = codecs.open('includes.tex', 'w', 'utf-8')
listoffiles = {}

catalog = parse_catalog_file(sys.argv[2])

# first, divide the monster files into texts.
texts = tree.findall('.//interlinear-text')

textnumberpattern = re.compile('\((\d+[a-z]?)\) *(.*)')
def parsetitle(title):
    textnumbermatch = textnumberpattern.search(title.text)
    if textnumbermatch:
        textnumber  = textnumbermatch.group(1)
        titlestring =  textnumbermatch.group(2)
    else:
        raise ValueError("No text number found for", title.text) 
            
    titlestring = titlestring.replace('&','\\&')
    titlestring = titlestring.replace('#','\\#')
    return (textnumber, titlestring)

for text in texts:
    # extract title info, add this info to our list of texts
    for item in text.findall(".//item"):
        if item.attrib['type'] == 'title':
            if item.attrib['lang'] == 'en':
                title = item
            elif item.attrib['lang'] == 'lhu':
                lahutitle = item
            else:
                raise ValueError("Language of title is neither English or Lahu")

    (textnumber, titlestring) = parsetitle(title)
    (lahutextnumber, lahutitlestring) = parsetitle(lahutitle)

    # if the text is not in the catalog, it is unused
    if textnumber not in catalog:
        continue

    if textnumber != lahutextnumber:
        raise ValueError("Lahu textnumber doesn't match English", textnumber, lahutextnumber)

    # instead of using the English title from the xml file,
    # we use the title from the catalog
    titlestring = catalog[textnumber][4]

    outputfilename = '%s.tex' % textnumber
    try:
        listoffiles[catalog[textnumber][3]] = textnumber
    except:
        # skip anything that is not sequenced
        pass

    # ok, let's parse each text and create the needed data structures
    # we create one output text for each input text
    OutLaTeX = codecs.open(outputfilename, 'w', 'utf-8')
    print >> OutLaTeX, '\section{%s}' % titlestring
    print >> OutLaTeX, '\\addlahutoc{section}{%s}' % lahutitlestring
    phrases = text.findall('.//phrases')
    print >> OutLaTeX, '\\begin{examples}'
    sentences = []
    for p in phrases:
        for s in p.findall('.//word/words'):
            # sentencenumber = s.find(".//item[@type='segnum']")
            print >> OutLaTeX, "\\item\n"
            print >> OutLaTeX, "\glll ",
            BaptistSentence = ''
            ChineseSentence = ''
            for w in s.findall('.//word'):
                for i in w.findall('.//item'):
                    if i.attrib['type'] in ['txt','punct']:
                        #form = codecs.encode(i.text,'utf8')
                        form = i.text
                        form = transduce(form,decompose)
                        form = escape(form)
                        BaptistSentence += ' %s' % transduce(form,baptist)
                        ChineseSentence += ' %s' % transduce(form,chinese)
            for level in ['txt', 'msa', 'gls']:
                for w in s.findall('.//word'):
                    itemToOutput = ' {}'
                    for i in w.findall('.//item'):
                        if i.attrib['type'] == 'punct':
                            if level in ['msa']:
                                form = ''
                            elif level in ['gls']:
                                form = ''
                            else:
                                form = str(i.text)
                        elif i.attrib['type'] == level:
                            form = str(i.text)
                            form = re.sub(r'/.*$','',form)
                        form = escape(form)
                        itemToOutput = ' {%s}' % form
                    print >> OutLaTeX, itemToOutput,
                print >> OutLaTeX
            print >> OutLaTeX, '\glt'
            print >> OutLaTeX, '\glend' + '\n'
            sentences.append([BaptistSentence,ChineseSentence])
    print >> OutLaTeX, '\\end{examples}'

    print >> OutLaTeX, '\subsection*{%s}' % 'Chinese'
    for i,sentence in enumerate(sentences):
        print >> OutLaTeX,  '[%s] %s \\\\\\relax' % (i+1, sentence[1].replace(' ,',',').replace(' .','.'))

    print >> OutLaTeX, '\subsection*{%s}' % 'Baptist'
    for i,sentence in enumerate(sentences):
        print >> OutLaTeX,  '[%s] %s \\\\\\relax' % (i+1, sentence[0].replace(' ,',',').replace(' .','.'))

    if textnumber in catalog:
        if catalog[textnumber][1] != '':
            if os.path.isfile(catalog[textnumber][1] + '.tex'):
                print >> OutLaTeX, '\subsection*{%s}' % 'Translation'
                print >> OutLaTeX, '\input{%s}' % catalog[textnumber][1]
            else:
                print '>>> translation file not found for #%s : %s.tex' % (textnumber, catalog[textnumber][1])
        else:
            print '>>>  no translation file listed for #%s : %s' % (textnumber, catalog[textnumber][0])

    OutLaTeX.close()

# write out the texts in order so they can be sucked in by
# LaTeX in order
for ((partno, part), (lpartno, lpart))  in zip(enumerate(structure),
                                               enumerate(lahu_structure)):
    print >> filestotex, '\part{%s}\n\\addlahutoc{part}{%s}' % (part[0], lpart[0])
    print "part %s. %s" % (partno+1, part[0])
    for ((chapterno, genre), (lchapterno, lgenre)) in zip(enumerate(part[1]),
                                                          enumerate(lpart[1])):
        print >> filestotex, '\chapter{%s}\n\\addlahutoc{chapter}{%s}' % (genre[1], lgenre[1])
        print "  chapter %s %s" % (chapterno+1, genre[1])
        for textnumber in sorted(listoffiles.keys()):
            if int(textnumber) == genre[0]:
                print >> filestotex, '\include{%s}' % listoffiles[textnumber]
                print "    %s " % textnumber
