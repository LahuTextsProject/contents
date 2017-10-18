#
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import codecs
import sys
import os
import re
import csv

from Transducer import transduce, baptist, chinese, decompose
from structure import structure, lahu_structure

def getTofCinfo(filename):
    try:
        TofCfile = codecs.open(filename, 'r', 'utf-8')
        csvfile = csv.reader(TofCfile, delimiter="\t")
    except IOError:
        message = 'Expected to be able to read %s, but it was not found or unreadable' % filename
        exit()
    except:
        raise

    try:
        TofCinfo = {}
        for row, values in enumerate(csvfile):
            # skip header line
            if row == 0:
                continue
            # are we using this text?
            if values[17] != 'y':
                continue
            try:
                TofCinfo[values[7]] = ["%s.%02d" % (values[11], int('0'+values[12])), values[15].replace('.rtf','').replace('.tex','').strip(), values[11]]
                TofCinfo[values[7]].append(float(TofCinfo[values[7]][0]))
            except:
                # raise
                print values

    except:
        raise
        print 'problem processing ToC csv file'
        exit()

    f.close()
    return TofCinfo

def escape(str):
    str = str.replace('&','\\&')
    str = str.replace('#','\\#')
    str = str.replace('_','\\_')
    #str = str.replace('-','\\-')
    return str

numberpattern = re.compile('\((\d+)\) *(.*)')

f = open(sys.argv[1], 'rt')
tree = ET.parse(f)
f.close()

# we'll be reorganizing (reordering) the files as they come in.
# (they don't come in in any useful order)
filestotex = codecs.open('includes.tex', 'w', 'utf-8')
listoffiles = {}

TofCinfo = getTofCinfo(sys.argv[2])

# first, divide the monster files into texts.
texts = tree.findall('.//interlinear-text')
offscale = 999

def parsetitle(title, inc_offscale_p):
    global offscale
    textnumbermatch = numberpattern.search(title.text)
    if textnumbermatch:
        textnumber  = textnumbermatch.group(1)
        titlestring =  textnumbermatch.group(2)
    else:
        if inc_offscale_p:
            offscale += 1
        textnumber  = offscale
        titlestring = title.text
            
    titlestring = titlestring.replace('&','\\&')
    titlestring = titlestring.replace('#','\\#')
    return (textnumber, titlestring, textnumber, titlestring)


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

    (textnumber, titlestring, textnumber, titlestring) = parsetitle(title, True)
    (lahutextnumber, lahutitlestring, lahutextnumber, lahutitlestring) = parsetitle(lahutitle, False)

    outputfilename = '%s.tex' % textnumber
    try:
        listoffiles[TofCinfo[textnumber][3]] = textnumber
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

    if textnumber in TofCinfo:
        if TofCinfo[textnumber][1] != '':
            if os.path.isfile(TofCinfo[textnumber][1] + '.tex'):
                print >> OutLaTeX, '\subsection*{%s}' % 'Translation'
                print >> OutLaTeX, '\input{%s}' % TofCinfo[textnumber][1]
            else:
                print '>>> translation file not found for #%s : %s.tex' % (textnumber, TofCinfo[textnumber][1])
        else:
            print '>>>  no translation file listed for #%s : %s' % (textnumber, TofCinfo[textnumber][0])

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
