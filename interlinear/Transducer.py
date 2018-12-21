# -*- coding: utf-8 -*-

import codecs
import csv, sys

reload(sys)
sys.setdefaultencoding('utf-8')

decompose = {'\xc9\x99': '\xc9\x99', '\xc5\x8d': 'o\xcc\x84', '\xc9\x9b': '\xc9\x9b', 'ch': 'ch',
             '\xc5\x8b': '\xc5\x8b', '\xc5\xab': 'u\xcc\x84', 'y\xc9\xa8': 'y\xc9\xa8',
             'j\xc9\xa8': 'j\xc9\xa8', 'aw': 'aw', 'ay': 'ay', '\xcc\x80': '\xcc\x80', 'kh': 'kh',
             '\xc3\xaa': 'e\xcc\x82', '\xcc\x80\xca\x94': '\xcc\x80\xca\x94', '\xc3\xa8': 'e\xcc\x80',
             '\xc5\xa1\xc9\xa8': '\xc5\xa1\xc9\xa8', '\xc3\xad': 'i\xcc\x81', '\xc3\xac': 'i\xcc\x80',
             '\xc3\xa2': 'a\xcc\x82', '\xc3\xa1': 'a\xcc\x81', '\xc3\xa0': 'a\xcc\x80', '\xc5\xa1': '\xc5\xa1',
             '\xc3\xbb': 'u\xcc\x82', '\xc9\xa8': '\xc9\xa8', '\xc3\xb9': 'u\xcc\x80', 'th': 'th',
             '\xcc\x81': '\xcc\x81', '\xc3\xb3': 'o\xcc\x81', '\xc3\xb2': 'o\xcc\x80', 'ph': 'ph',
             '\xc3\xb4': 'o\xcc\x82', 'g\xcc\x88': 'g\xcc\x88', 'we': 'we', '\xc4\xab': 'i\xcc\x84',
             '\xca\x94': '\xca\x94', 'c\xc9\xa8': 'c\xc9\xa8', '\xc3\xa9': 'e\xcc\x81', 'wi': 'wi',
             '\xc9\x94': '\xc9\x94', 'y': 'y', '\xe2\x80\xa6': '\xe2\x80\xa6', 'e': 'e', '\xc4\x93': 'e\xcc\x84',
             '\xc4\x81': 'a\xcc\x84', 'w\xc9\x9b': 'w\xc9\x9b', '\xc3\xba': 'u\xcc\x81', '\xc3\xae': 'i\xcc\x82',
             'a': 'a', 'c': 'c', 'b': 'b', '\xcc\x82': '\xcc\x82', 'd': 'd', 'g': 'g', 'f': 'f', 'i': 'i', 'h': 'h',
             'k': 'k', 'j': 'j', 'm': 'm', 'l': 'l', 'o': 'o', 'n': 'n', 'q': 'q', 'p': 'p', 'u': 'u', 't': 't',
             'v': 'v', 'w': 'w', '\xcc\x82\xca\x94': '\xcc\x82\xca\x94', 'qh': 'qh', '\xcc\x84': '\xcc\x84',
             '-': '-', ',': ',', '.': '.', '"': '"', "'": "'", ":": ":",
             'ch\xc9\xa8': 'ch\xc9\xa8'}

baptist = {'ch': 'ch', 'a\xcc\x81w': 'ao\xc2\xaf', 'a\xcc\x81y': 'ai\xc2\xaf',
           '\xcc\x80\xca\x94': '\xe2\x80\xb8', '\xc5\xa1\xc9\xa8': 'suh', 'pu': 'pfuh', 'g': 'g', 'th': 'ht',
           'ph': 'hp', 'g\xcc\x88': 'g\xe2\x80\x99', 'c\xc9\xa8': 'tcuh', '\xcc\x84': '\\protect\\underline{\\protect\\phantom{x}}',
           '\xc9\x94': 'aw', 'a\xcc\x82y': 'ai\xcb\x87', '\xcc\x82': '\xcb\x87', 'a\xcc\x82w': 'ao\xcb\x87', 'b': 'b',
           'd': 'd', 'f': 'f', 'h': 'h', 'j': 'j', 'l': 'l', 'n': 'n', 'mu': 'mvuh', 'p': 'p', 't': 't', 'v': 'v',
           '\xcc\x82\xca\x94': '\xcb\x86', 'qh': 'hk\xe2\x80\x99', '\xc9\x99': 'eu', '\xc9\x9b': 'eh', '\xc5\x8b': 'ng',
           'y\xc9\xa8': 'zuh', 'j\xc9\xa8': 'dzuh', 'a\xcc\x84w': 'ao\\protect\\underline{\\protect\\phantom{x}}', 'aw': 'ao', 'ay': 'ai',
           'p\xc9\xa8': 'pu', 'ni': 'nyi', 'a\xcc\x84y': 'ai\\protect\\underline{\\protect\\phantom{x}}', '\xc5\xa1': 'sh',
           '\xc9\xa8': 'uh', 'ch\xc9\xa8': 'tsuh', 'we': 'o-e', 'wi': 'u-i', 'bu': 'bvuh',
           'a\xcc\x80w': 'ao\xe1\xb5\xa5', '\xe2\x80\xa6': '\xe2\x80\xa6', 'a\xcc\x80y': 'ai\xe1\xb5\xa5',
           'w\xc9\x9b': 'aweh', 'phu': 'hpfuh', 'a': 'a', 'c': 'c', 'e': 'e', '\xcc\x80': '\xe1\xb5\xa5',
           '\xcc\x81': '\xc2\xaf', 'i': 'i', 'k': 'k', 'kh': 'hk', 'm': 'm', 'o': 'o', 'q': 'k\xe2\x80\x99',
           'u': 'uh',
           '-': '-', ',': ',', '.': '.', '"': '"', "'": "'", ":": ":",
           'y': 'y', '\xc4\xb1': 'i'}

chinese = {'ch': 'ch', 'a\xcc\x81w': 'aoq', 'a\xcc\x81y': 'aiq', '\xcc\x80\xca\x94': 'r',
           '\xc5\xa1\xc9\xa8': 'seu', '\xc3\xa2': 'ad', '\xc3\xa2w': 'aod', 'th': 'th', 'ph': 'ph',
           '\xc3\xa2y': 'aid', 'a': 'a', 'c\xc9\xa8': 'zeu', '\xcc\x84': 'f', 'y\xc9\xa8': 'reu', 'a\xcc\x82y': 'aid',
           '\xcc\x82': 'd', 'a\xcc\x82w': 'aod', 'b': 'b', 'd': 'd', 'f': 'f', 'h': 'h', 'j': 'j', 'l': 'l', 'n': 'n',
           'p': 'p', 't': 't', 'v': 'v', '\xcc\x82\xca\x94': 't', 'qh': 'qh', '\xc9\x99': 'eu', '\xc9\x9b': 'ie',
           '\xc5\x8b': 'ng', '\xc9\x94': 'aw', 'j\xc9\xa8': 'dzeu', 'a\xcc\x84w': 'aof', 'aw': 'ao', 'ay': 'ai',
           'a\xcc\x84y': 'aif', '\xc5\xa1': 'sh', '\xc9\xa8': 'eu', 'ch\xc9\xa8': 'zheu', 'we': 'ue', 'wi': 'ui',
           'g': 'g', 'a\xcc\x80w': 'aol', '\xe2\x80\xa6': '\xe2\x80\xa6', 'a\xcc\x80y': 'ail', 'w\xc9\x9b': 'uie',
           'g\xcc\x88': 'x', 'c': 'c', 'e': 'e', '\xcc\x80': 'l', '\xcc\x81': 'q', 'i': 'i', 'k': 'k', 'kh': 'kh',
           'm': 'm', 'o': 'o', 'q': 'q', 'u': 'u', 'y': 'y', '\xc4\xb1': 'i',
           '-': '-', ',': ',', '.': '.', '"': '"', "'": "'", ":": ":",
           } #includes diphthongs


def runop(filename, dict):
    frame = []
    for line in open(filename, 'rU'):
        frame.append(line.split())
    newframe = []
    for line in frame:
        newline = []
        for word in line:
            if word[0].isupper() == True:
                newword = ''
                newword += word[0].lower()
                newword += word[1:]
                newword = transduce(newword, decompose)
                newerword = ''
                newerword += newword[0].upper()
                newerword += newword[1:]
                newline.append(newerword)
            else:
                newline.append(transduce(word, decompose))
        newframe.append(newline)
    newerframe = []
    for line in newframe:
        newline = []
        for word in line:
            if word[0].isupper() == True:
                newword = ''
                newword += word[0].lower()
                newword += word[1:]
                newword = transduce(newword, dict)
                newerword = ''
                newerword += newword[0].upper()
                newerword += newword[1:]
                newline.append(newerword)
            else:
                newline.append(transduce(word, dict))
        newerframe.append(newline)
    for line in newerframe:
        for word in line:
            print word,
        print


def findConstituent(token, kys):
    for x in kys:
        # stick asterisk in front of both strings so we match only on initial substring
        if '*' + x in '*' + token:
            return x
    return None


def transduce(token, twolevels):
    kys = sorted(twolevels, key=len, reverse=True)
    result = ''
    casecounter = 0
    lowtoken = ''
    final = ''
    if token != '':
        if token[0].isupper() == True:
            lowtoken += token[0].lower()
            lowtoken += token[1:]
            casecounter += 1
        else:
            lowtoken += token[:]
    else:
        lowtoken += token[:]
    while lowtoken != '':
        constituent = findConstituent(lowtoken, kys)
        if constituent:
            result += twolevels[constituent]
            lowtoken = lowtoken.replace(constituent, '', 1)
        else:
        #            print result,'stuck at ',token,[token]
        #            return None
            return ''

    if casecounter == 0:
        final += result[:]
    if casecounter == 1:
        final += result[0].upper()
        final += result[1:]

    return final

def transduce_string(string, twolevels):
    new = ''
    for token in string.split():
        new += transduce(token, twolevels)
        new += ' '
    return new[:-1]
