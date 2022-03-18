#
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import sys
import os
import re
import csv
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
        catalog_file = open(filename, 'r')
    except IOError:
        message = 'Expected to be able to read %s, but it was not found or unreadable' % filename
        exit()

    csvfile = csv.reader(catalog_file, delimiter="\t")
    catalog = {}
    # skip header row
    next(csvfile)
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

with open(sys.argv[1], 'r') as f:
    tree = ET.parse(f)

# we'll be reorganizing (reordering) the files as they come in.
# (they don't come in in any useful order)
filestotex = open('includes.tex', 'w')
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

sentence_pattern = re.compile('(\d+)\. *(.*)')
# read all sentences from the translation file.
def read_translation_sentences(translation_file):
    sentences = []
    sentence = None
    while True:
        line = translation_file.readline()
        match = sentence_pattern.match(line)
        if line == '':
            # end of file
            if sentence:
                sentences.append(sentence)
            break
        elif match:
            if sentence:
                sentences.append(sentence)
            sentence = match.group(2)
        elif sentence and (line != '\n'):
            sentence += ' '
            sentence += line
    return sentences

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

    # open the translation file to try and slurp up the translated line.
    # translation_file_name = catalog[textnumber][1]
    # translation_file = open('%s.tex' % translation_file_name, "r")
    # translation_sentences = read_translation_sentences(translation_file)
    # translation_file.close()
    # num_translations = len(translation_sentences)

    # ok, let's parse each text and create the needed data structures
    # we create one output text for each input text
    OutLaTeX = open(outputfilename, 'w')
    print('\setcounter{equation}{0}', file=OutLaTeX)
    print('\setcounter{footnote}{0}', file=OutLaTeX)
    print('\section{%s}' % titlestring, file=OutLaTeX)
    print('\\thispagestyle{plain}', file=OutLaTeX)
    print('\label{sec:%s}' % textnumber, file=OutLaTeX)
    print('\\addlahutoc{section}{%s}' % lahutitlestring, file=OutLaTeX)
    # if with_baptist:
    #     print('\\addbaptisttoc{section}{%s}' % \, file=OutLaTeX)
    #         transduce_string(transduce_string(lahutitlestring, decompose), baptist)
    # if with_chinese:
    #     print('\\addchinesetoc{section}{%s}' % \, file=OutLaTeX)
    #     transduce_string(transduce_string(lahutitlestring, decompose), chinese)
    phrases = text.findall('.//phrases/word')
    num_phrases = len(phrases)
    print('\\begin{examples}', file=OutLaTeX)
    # sentences = []
    for p in phrases:
        sentencenumber = p.find(".//item[@type='segnum']")
        try:
            sentencenumber = sentencenumber.text
        except:
            sentencenumber = 'not found'
        # print(f'{textnumber}, {titlestring}: sentence {sentencenumber}')
        for s in p.findall('.//words'):
            print("\\item\n", file=OutLaTeX)
            print("\glll ", end='', file=OutLaTeX)
            # if with_baptist:
            #     BaptistSentence = ''
            # if with_chinese:
            #     ChineseSentence = ''
            for w in s.findall('.//word'):
                for i in w.findall('.//item'):
                    if i.attrib['type'] in ['txt','punct']:
                        #form = encode(i.text,'utf8')
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
                    print(itemToOutput, end='', file=OutLaTeX)
                print('', file=OutLaTeX)
                # print(f'{level} ', end='')
        # try:
        #     translation_sentence = translation_sentences.pop(0)
        # except IndexError:
        #     translation_sentence = 'Ran out of free translation sentences!'
        #print('\glt `', file=OutLaTeX) + translation_sentence + "'", file=OutLaTeX)
        print(' \glot {}', file=OutLaTeX)
        print('\glend' + '\n', file=OutLaTeX)
        # print(f'ended {sentencenumber}')
    print('\\end{examples}', file=OutLaTeX)

    # # check if we have more free translation lines than there are interlinear sentences.
    # if num_phrases > num_translations:
    #     print(translation_file_name + " not enough free translation sentences to match the interlinear!")
    # elif num_phrases < num_translations:
    # # if translation_sentences != []:
    #     print(translation_file_name + " more free translation sentences than there are interlinear sentences!")
    # else:
    #     print(translation_file_name + " translation sentences and interlinear sentences match up!")
    # print('phrases: %s translations: %s diff: %s' % (num_phrases, num_translations, num_phrases - num_translations))


    # if with_chinese:
    #     print('\subsection*{%s}' % 'Chinese', file=OutLaTeX)
    #     for i,sentence in enumerate(sentences):
    #         print( '[%s] %s \\\\\\relax' % (i+1, sentence[1].replace(' ,',',').replace(' .','.')), file=OutLaTeX)
    # if with_baptist:
    #     print('\subsection*{%s}' % 'Baptist', file=OutLaTeX)
    #     for i,sentence in enumerate(sentences):
    #         print( '[%s] %s \\\\\\relax' % (i+1, sentence[0].replace(' ,',',').replace(' .','.')), file=OutLaTeX)

    if textnumber in catalog:
        if catalog[textnumber][1] != '':
            if os.path.isfile(catalog[textnumber][1] + '.tex'):
                print('\subsection*{%s}' % 'Translation', file=OutLaTeX)
                # English titles is redundant here. don't use...
                # print(r'\textbf{%s}'% titlestring, file=OutLaTeX)
                print('\input{%s}' % catalog[textnumber][1], file=OutLaTeX)
            else:
                print('>>> translation file not found for #%s : %s.tex' % (textnumber, catalog[textnumber][1]))
        else:
            print('>>>  no translation file listed for #%s : %s' % (textnumber, catalog[textnumber][0]))

    OutLaTeX.close()

# write out the texts in order so they can be sucked in by
# LaTeX in order
for ((partno, part), (lpartno, lpart)) in zip(enumerate(structure),
                                              enumerate(lahu_structure)):
    partname = part[0]
    lahupartname = lpart[0]
    print('\part{%s}' % partname, file=filestotex)
    print('\\addlahutoc{part}{%s}' % lahupartname, file=filestotex)
    print('\label{part:%s}' % partname, file=filestotex)
    # if with_baptist:
    #     print('\\addbaptisttoc{part}{%s}' % \, file=filestotex)
    #         transduce_string(transduce_string(lahupartname, decompose), baptist)
    # if with_chinese:
    #     print('\\addchinesetoc{part}{%s}' % \, file=filestotex)
    #         transduce_string(transduce_string(lahupartname, decompose), chinese)
    print("part %s. %s" % (partno+1, partname))
    for ((chapterno, genre), (lchapterno, lgenre)) in zip(enumerate(part[1]),
                                                          enumerate(lpart[1])):
        chaptername = genre[1]
        lahuchaptername = lgenre[1]
        print('\chapter{%s}' % chaptername, file=filestotex)
        print('\\addlahutoc{chapter}{%s}' % lahuchaptername, file=filestotex)
        print('\label{chapter:%s}' % chaptername.replace('"', ''), file=filestotex)
        # if with_baptist:
        #     print('\\addbaptisttoc{chapter}{%s}' % \, file=filestotex)
        #         transduce_string(transduce_string(lahuchaptername, decompose), baptist)
        # if with_chinese:
        #     print('\\addchinesetoc{chapter}{%s}' % \, file=filestotex)
        #         transduce_string(transduce_string(lahuchaptername, decompose), chinese)
        print("  chapter %s %s" % (chapterno+1, chaptername))
        for textnumber in sorted(listoffiles.keys()):
            if int(textnumber) == genre[0]:
                print('\include{%s}' % listoffiles[textnumber], file=filestotex)
                print("    %s " % textnumber)

form_class_info = parse_form_class_file(sys.argv[3])
abbreviation_file = open('abbreviations.tex', 'w')
for key, value in form_class_info.items():
    # periods really screw up the sorting.
    print('\\newacronym[sort=%s]{%s}{%s}{%s}' \
        % (value[1].replace("\\textsubscript{v", "v")
           .replace("\\textsubscript{", "a")
           .replace("}", "")
           .replace("\\textbf{", ""),
           key, value[1], value[0]), file=abbreviation_file)
abbreviation_file.close()

def parse_glosses_by_frequency(filename):
    # we assume that the most frequent glosses for a word are read first
    # cf. triples.csv
    with open(filename, 'r') as f:
        csvfile = csv.reader(f, delimiter='\t')
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
    for key, value in special.items():
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
    for key, value in special.items():
        string = string.replace(key, value)
    return string

lexicon = parse_glosses_by_frequency(sys.argv[4])
def output_glossary(filename, sort_key, language=None):
    glossary_file = open(filename, 'w')
    j = 0
    for key, value in lexicon.items():
        if language == baptist:
            form = transduce_string(transduce_string(key, decompose), language)
            print(r'\newglossaryentry{%s%s}{name=%s, type=%s, sort=%s, description = {' \
                % ("baptist", j,
                   form,
                   "baptist",
                   sort_key(key)), file=glossary_file)
        elif language == chinese:
            form = transduce_string(transduce_string(key, decompose), language)
            print(r'\newglossaryentry{%s%s}{name=%s, type=%s, sort=%s, description = {' \
                % ("chinese", j,
                   form,
                   "chinese",
                   sort_key(form)), file=glossary_file)
        else:
            print(r'\newglossaryentry{%s}{name=%s, type=lexicon, sort=%s, description = {' % (key, key, sort_key(key)), file=glossary_file)
        j += 1
        gloss_dict = {}
        for gloss in value:
            gloss_dict.setdefault(gloss[0], []).append(gloss[1])
        i = 1
        if len(gloss_dict.keys()) == 1:
            key = list(gloss_dict.keys())[0]
            glossary_file.write('(\gls{%s})~%s' % (key, ', '.join(gloss_dict[key])))
        else:
            for key, senses in gloss_dict.items():
                if i > 1:
                    print(';', file=glossary_file)
                glossary_file.write('%d.~(\gls{%s})~%s' % (i, key, ', '.join(senses)))
                i += 1
        print(r'}}', file=glossary_file)
    glossary_file.close()
output_glossary('lexical_glossary.tex', make_sort_string)
output_glossary('blexical_glossary.tex', make_baptist_sort_string, language=baptist)
output_glossary('clexical_glossary.tex', lambda x: x, language=chinese)
