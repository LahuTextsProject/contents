#
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import codecs
import sys
import os
import re
import unicodecsv as csv
import argparse

from Transducer import transduce, transduce_string, baptist, chinese, decompose
from structure import structure, lahu_structure
from formclass import parse_form_class_file
from collections import OrderedDict

parser = argparse.ArgumentParser(description='Generate interlinear LaTeX.')
#parser.add_argument('-b', '--with-baptist', action='store_true')
#parser.add_argument('-c', '--with-chinese', action='store_true')
parser.add_argument('args', nargs=5)

parsed_args = parser.parse_args()
# with_baptist = parsed_args.with_baptist
# with_chinese = parsed_args.with_chinese

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
    for info in csvfile:
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
    print >> OutLaTeX, '\setcounter{equation}{0}'
    print >> OutLaTeX, '\section{%s}' % titlestring
    print >> OutLaTeX, '\label{sec:%s}' % textnumber
    print >> OutLaTeX, '\\addlahutoc{section}{%s}' % lahutitlestring
    # if with_baptist:
    #     print >> OutLaTeX, '\\addbaptisttoc{section}{%s}' % \
    #         transduce_string(transduce_string(lahutitlestring, decompose), baptist)
    # if with_chinese:
    #     print >> OutLaTeX, '\\addchinesetoc{section}{%s}' % \
    #     transduce_string(transduce_string(lahutitlestring, decompose), chinese)
    phrases = text.findall('.//phrases')
    print >> OutLaTeX, '\\begin{examples}'
    sentences = []
    for p in phrases:
        for s in p.findall('.//word/words'):
            # sentencenumber = s.find(".//item[@type='segnum']")
            print >> OutLaTeX, "\\item\n"
            print >> OutLaTeX, "\glll ",
            # if with_baptist:
            #     BaptistSentence = ''
            # if with_chinese:
            #     ChineseSentence = ''
            for w in s.findall('.//word'):
                for i in w.findall('.//item'):
                    if i.attrib['type'] in ['txt','punct']:
                        #form = codecs.encode(i.text,'utf8')
                        form = i.text
                        form = transduce(form,decompose)
                        form = escape(form)
                        # if with_baptist:
                        #     BaptistSentence += ' %s' % transduce(form,baptist)
                        # if with_chinese:
                        #     ChineseSentence += ' %s' % transduce(form,chinese)
            for level in ['txt', 'msa', 'gls']:
                for w in s.findall('.//word'):
                    itemToOutput = ' {}'
                    for i in w.findall('.//item'):
                        if i.attrib['type'] == 'punct' or i.text == '--':
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
                        ## this is hacky
                        if i.attrib['type'] == 'msa' and level == 'msa':
                            form = '\gls{%s}' % form.strip()
                        itemToOutput = ' {%s}' % form
                    print >> OutLaTeX, itemToOutput,
                print >> OutLaTeX
            print >> OutLaTeX, '\glt'
            print >> OutLaTeX, '\glend' + '\n'
            # sentences.append([BaptistSentence if with_baptist else None, \
            #                   ChineseSentence if with_chinese else None])
    print >> OutLaTeX, '\\end{examples}'

    # if with_chinese:
    #     print >> OutLaTeX, '\subsection*{%s}' % 'Chinese'
    #     for i,sentence in enumerate(sentences):
    #         print >> OutLaTeX,  '[%s] %s \\\\\\relax' % (i+1, sentence[1].replace(' ,',',').replace(' .','.'))
    # if with_baptist:
    #     print >> OutLaTeX, '\subsection*{%s}' % 'Baptist'
    #     for i,sentence in enumerate(sentences):
    #         print >> OutLaTeX,  '[%s] %s \\\\\\relax' % (i+1, sentence[0].replace(' ,',',').replace(' .','.'))

    if textnumber in catalog:
        if catalog[textnumber][1] != '':
            if os.path.isfile(catalog[textnumber][1] + '.tex'):
                print >> OutLaTeX, '\subsection*{%s}' % 'Translation'
                # make sure our English titles are consistent
                print >> OutLaTeX, r'\textbf{%s}'% titlestring
                print >> OutLaTeX, '\input{%s}' % catalog[textnumber][1]
            else:
                print '>>> translation file not found for #%s : %s.tex' % (textnumber, catalog[textnumber][1])
        else:
            print '>>>  no translation file listed for #%s : %s' % (textnumber, catalog[textnumber][0])

    OutLaTeX.close()

# write out the texts in order so they can be sucked in by
# LaTeX in order
for ((partno, part), (lpartno, lpart)) in zip(enumerate(structure),
                                              enumerate(lahu_structure)):
    partname = part[0]
    lahupartname = lpart[0]
    print >> filestotex, '\part{%s}' % partname
    print >> filestotex, '\label{part:%s}' % partname
    print >> filestotex, '\\addlahutoc{part}{%s}' % lahupartname
    # if with_baptist:
    #     print >> filestotex, '\\addbaptisttoc{part}{%s}' % \
    #         transduce_string(transduce_string(lahupartname, decompose), baptist)
    # if with_chinese:
    #     print >> filestotex, '\\addchinesetoc{part}{%s}' % \
    #         transduce_string(transduce_string(lahupartname, decompose), chinese)
    print "part %s. %s" % (partno+1, partname)
    for ((chapterno, genre), (lchapterno, lgenre)) in zip(enumerate(part[1]),
                                                          enumerate(lpart[1])):
        chaptername = genre[1]
        lahuchaptername = lgenre[1]
        print >> filestotex, '\chapter{%s}' % chaptername
        print >> filestotex, '\label{chapter:%s}' % chaptername.replace('"', '')
        print >> filestotex, '\\addlahutoc{chapter}{%s}' % lahuchaptername
        # if with_baptist:
        #     print >> filestotex, '\\addbaptisttoc{chapter}{%s}' % \
        #         transduce_string(transduce_string(lahuchaptername, decompose), baptist)
        # if with_chinese:
        #     print >> filestotex, '\\addchinesetoc{chapter}{%s}' % \
        #         transduce_string(transduce_string(lahuchaptername, decompose), chinese)
        print "  chapter %s %s" % (chapterno+1, chaptername)
        for textnumber in sorted(listoffiles.keys()):
            if int(textnumber) == genre[0]:
                print >> filestotex, '\include{%s}' % listoffiles[textnumber]
                print "    %s " % textnumber

form_class_info = parse_form_class_file(sys.argv[3])
abbreviation_file = codecs.open('abbreviations.tex', 'w', 'utf-8')
for key, value in form_class_info.iteritems():
    # periods really screw up the sorting.
    print >> abbreviation_file, '\\newacronym[sort=%s]{%s}{%s}{%s}' \
        % (value[1].replace("\\textsubscript{v", "v")
           .replace("\\textsubscript{", "a")
           .replace("}", "")
           .replace("\\textbf{", ""),
           key, value[1], value[0])
abbreviation_file.close()

def parse_glosses_by_frequency(filename):
    # we assume that the most frequent glosses for a word are read first
    # cf. triples.csv
    with open(filename, 'rt') as f:
        csvfile = csv.reader(f, delimiter='\t', encoding='utf-8')
        lexicon = {}
        for info in csvfile:
            if len(info) != 4:
                continue
            word = info[1].strip()
            formclass = info[2].strip()
            gloss = info[3].strip()
            lexicon[word] = lexicon.get(word, []) + [[formclass, gloss]]
        return lexicon

# our alphabet ordering:
# a b c ch d e ɛ ə f g g̈ h i ɨ j k kh l m n ŋ o ɔ p ph q qh š
# t th u v w y ʔ
# tones: ´ ` ¯ ^ ^ʔ `ʔ
# TODO implement this if latex can't do it
# lahu_alphabet = ['a', 'b', 'c', 'ch', 'd', 'e', 'ɛ', 'ə', 'f', 'g', 'g̈', 'h', 'i', 'ɨ', 'j', 'k', 'kh', 'l', 'm', 'n', 'ŋ', 'o', 'ɔ', 'p', 'ph', 'q', 'qh', 'š', 't', 'th', 'u', 'v', 'w', 'y', 'ʔ']

# lahu_tones = ['´', '`', '^', '¯', '^ʔ', '`ʔ']

# def lahu_alphabet_sort(string):
#     tone_count = len(lahu_tones)
#     return len(lahu_tones)
class _OrderedDictMaker(object):
    def __getitem__(self, keys):
        if not isinstance(keys, tuple):
            keys = (keys,)
        assert all(isinstance(key, slice) for key in keys)

        return OrderedDict([(k.start, k.stop) for k in keys])

ordereddict = _OrderedDictMaker()

def make_sort_string(string):
    # HACK: this might not work 100% of the time
    special = ordereddict[
        'a': 'aa', 'b': 'ba', 'c': 'ca', 'cah': 'cz', 'd': 'da',
        'e': 'ea', 'ɛ': 'eb', 'ə': 'ec', 'f': 'fa', 'g': 'ga',
        'g̈': 'g̈a', 'h': 'ha', 'i': 'ia', 'ɨ': 'iz', 'j': 'ja',
        'k': 'ka', 'kaha': 'kz', 'l': 'la', 'n': 'na', 'ŋ':
        'nz', 'o': 'oa', 'ɔ': 'oz', 'p': 'pa', 'paha': 'pz',
        'q': 'qa', 'qaha': 'qz', 's': 'sa', 'š': 'sz', 't':
        'ta', 'taha': 'tz', 'u': 'ua', 'v': 'va', 'w': 'wa',
        'y': 'ya', 'z': 'za', 'ʔ': 'zz',
        'á': 'ab', 'â': 'ac', 'à': 'ad', 'ā': 'ae',
        'aczz': 'af', 'adzz': 'ag', 'ã': 'ah',
        'é': 'eb', 'ê': 'ec', 'è': 'ed', 'ē': 'ee',
        'eczz': 'ef', 'edzz': 'eg', 'ẽ': 'ef',
        'í': 'ib', 'î': 'ic', 'ì': 'id', 'ī': 'ie',
        'iczz': 'if', 'idzz': 'ig', 'ĩ': 'ih',
        'ó': 'ob', 'ô': 'oc', 'ò': 'od', 'ō': 'oe',
        'oczz': 'of', 'odzz': 'og', 'õ': 'oh',
        'ú': 'ub', 'û': 'uc', 'ù': 'ud', 'ū': 'ue',
        'uczz': 'uf', 'udzz': 'ug', 'ũ': 'uh']
    string = string.lower()
    for key, value in special.iteritems():
        string = string.replace(key, value)
    return string

def make_baptist_sort_string(string):
    special = ordereddict[
        'a': 'ac', 'b': 'ba', 'c': 'ca', 'cah': 'cz', 'd': 'da',
        'e': 'ec', 'ə': 'ez', 'f': 'fa', 'g': 'ga',
        'g̈': 'g̈a', 'h': 'ha', 'i': 'ia', 'ɛ': 'emc', 'j': 'dz',
        'k': 'ka', 'kaha': 'kb', 'q': 'kc', 'kcha': 'kd',
        'l': 'la', 'n': 'na', 'ŋ':
        'nz', 'o': 'oc', 'ɔ': 'au', # u will handle adding c to this
        'p': 'pa', 'paha': 'pz',
        's': 'sa', 'š': 'sz', 't': 'ta', 'taha': 'tz',
        'u': 'uc', 'ɨ': 'uic', 'v': 'va',
        # since w is usually translated o- or aw- or u
        'wem': 'aucem', 'we': 'oce', 'wi': 'uc',
        'y': 'za', 'z': 'za', 'ʔ': 'zz',
        # tones on vowels
        'á': 'ab', 'â': 'aa', 'à': 'ae', 'ā': 'ad',
        'aazz': 'af', 'aezz': 'ag', 'ã': 'ah',
        'é': 'eb', 'ê': 'ea', 'è': 'ee', 'ē': 'ed',
        'eazz': 'ef', 'eezz': 'eg', 'ẽ': 'eh',
        'í': 'ib', 'î': 'ia', 'ì': 'ie', 'ī': 'id',
        'iazz': 'if', 'iezz': 'ig', 'ĩ': 'ih',
        'ó': 'ob', 'ô': 'oa', 'ò': 'oe', 'ō': 'od',
        'oazz': 'of', 'oezz': 'og', 'õ': 'oh',
        'ú': 'ub', 'û': 'ua', 'ù': 'ue', 'ū': 'ud',
        'uazz': 'uf', 'uezz': 'ug', 'ũ': 'uh',
        # detachable tones for non latin characters
        '́' : '1' ,  '̂': '2' , '̀' : '3', '̄' : '4',
        '2zz' : '5', '3zz' : '6',
        'auc1' : 'aub', 'auc2' : 'aua', 'auc3' : 'aue', 'auc4' : 'aud',
        'auc5' : 'auf', 'auc6' : 'aug',
        'uic1' : 'uib', 'uic2' : 'uia', 'uic3' : 'uie', 'uic4' : 'uid',
        'uic5' : 'uif', 'uic6' : 'uig',
        'emc1' : 'emb', 'emc2' : 'ema', 'emc3' : 'eme', 'emc4' : 'emd',
        'emc5' : 'emf', 'emc6' : 'emg',
        # imperfectly phonemicized things:
        # cɨ > tcuh
        'caui' : 'tbui',
        # chɨ > tsuh
        'czaui' : 'tcaui']
    string = string.lower()
    for key, value in special.iteritems():
        string = string.replace(key, value)
    return string

lexicon = parse_glosses_by_frequency(sys.argv[4])
def output_glossary(filename, sort_key, language=None):
    glossary_file = codecs.open(filename, 'w', 'utf-8')
    j = 0
    for key, value in lexicon.iteritems():
        if language == baptist:
            form = transduce_string(transduce_string(key, decompose), language)
            print >> glossary_file, r'\newglossaryentry{%s%s}{name=%s, type=%s, sort=%s, description = {' \
                % ("baptist", j,
                   form,
                   "baptist",
                   sort_key(key))
        elif language == chinese:
            form = transduce_string(transduce_string(key, decompose), language)
            print >> glossary_file, r'\newglossaryentry{%s%s}{name=%s, type=%s, sort=%s, description = {' \
                % ("chinese", j,
                   form,
                   "chinese",
                   sort_key(form))
        else:
            print >> glossary_file, r'\newglossaryentry{%s}{name=%s, type=lexicon, sort=%s, description = {' % (key, key, sort_key(key))
        j += 1
        gloss_dict = {}
        for gloss in value:
            gloss_dict.setdefault(gloss[0], []).append(gloss[1])
        i = 1
        if len(gloss_dict.keys()) == 1:
            key = gloss_dict.keys()[0]
            glossary_file.write('(\gls{%s})~%s' % (key, ', '.join(gloss_dict[key])))
        else:
            for key, senses in gloss_dict.iteritems():
                if i > 1:
                    print >> glossary_file, ';'
                glossary_file.write('%d.~(\gls{%s})~%s' % (i, key, ', '.join(senses)))
                i += 1
        print >> glossary_file, r'}}'
    glossary_file.close()
output_glossary('lexical_glossary.tex', make_sort_string)
output_glossary('blexical_glossary.tex', make_baptist_sort_string, language=baptist)
output_glossary('clexical_glossary.tex', lambda x: x, language=chinese)
