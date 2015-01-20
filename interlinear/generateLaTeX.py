#
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import codecs
import sys
import re

from Transducer import transduce,baptist,chinese,decompose

numberpattern = re.compile('\((\d+)\) *(.*)')

f = open(sys.argv[1], 'rt')
tree = ET.parse(f)
f.close()

# we'll be reorganizing (reordering) the files as they come in.
# (they don't come in in any useful order)
filestotex = codecs.open('includes.tex', 'w', 'utf-8')
listoffiles = {}

# first, divide the monster files into texts.
texts = tree.findall('.//interlinear-text')
offscale = 999
for text in texts:

    # extract title info, add this info to our list of texts
    title = text.find(".//item[@type='title']")
    textnumbermatch = numberpattern.search(title.text)
    
    if textnumbermatch:
        textnumber  = textnumbermatch.group(1)
        titlestring =  textnumbermatch.group(2)
    else:
        offscale += 1
        textnumber  = offscale
        titlestring = title.text

    titlestring = titlestring.replace('&','\\&')
    titlestring = titlestring.replace('#','\\#')
    outputfilename = '%s.tex' % textnumber
    listoffiles[int(textnumber)] = textnumber

    # ok, let's parse each text and create the needed data structures
    # we create one output text for each input text
    O = codecs.open(outputfilename, 'w', 'utf-8')
    print >> O, '\chapter{%s}' % titlestring
    phrases = text.findall('.//phrases')
    print >> O, '\\begin{examples}'
    sentences = []
    for p in phrases:
        for s in p.findall('.//word/words'):
            sentencenumber = s.find(".//item[@type='segnum']")
            print >> O, "\\item\n"
            print >> O, "\glll ",
            BaptistSentence = ''
            ChineseSentence = ''
            for w in s.findall('.//word'):
                for i in w.findall('.//item'):
                    if i.attrib['type'] in ['txt','punct']:
                        #form = codecs.encode(i.text,'utf8')
                        form = i.text
                        form = transduce(form,decompose)
                        form = form.replace('&','\\&')
                        form = form.replace('#','\\#')
                        form = form.replace('_','\\_')
                        #form = form.replace('-','\\-')
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
                        form = form.replace('&','\\&')
                        form = form.replace('#','\\#')
                        form = form.replace('_','\\_')
                        #form = form.replace('-','\\-')
                        itemToOutput = ' {%s}' % form
                    print >> O, itemToOutput,
                print >> O
            print >> O, '\glt'
            print >> O, '\glend' + '\n'
            sentences.append([BaptistSentence,ChineseSentence])
    print >> O, '\\end{examples}'

    print >> O, '\subsection*{%s}' % 'Chinese'
    for i,sentence in enumerate(sentences):
        print >> O,  '[%s] %s \n' % (i+1, sentence[1])

    print >> O, '\subsection*{%s}' % 'Baptist'
    for i,sentence in enumerate(sentences):
        print >> O,  '[%s] %s \n' % (i+1, sentence[0])

    O.close()

# write out the texts in order so they can be sucked in by
# LaTex in order
for textnumber in sorted(listoffiles.keys()):
    print >> filestotex, '\include{%s}' % textnumber

