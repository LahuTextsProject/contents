#!usr/bin/env python

import sys, os, codecs
import unicodedata
import xml.etree.ElementTree as ET
from Transducer import transduce, chinese, baptist, decompose


def main():
    #  for line in open('lahu_writing.txt','rU'):
    #    for word in line.split():
    #      print word,
    #      print transduce(word,decompose),
    #      print transduce(transduce(word,decompose),chinese),
    #      print transduce(transduce(word,decompose),baptist)

    f = open('4testLahuTexts.xml', 'r')
    tree = ET.parse(f)
    f.close()
    for node in tree.findall('.//word/words/word/item'):
        if node.attrib['type'] == 'txt':
            # form = codecs.encode(node.text,'utf8')
            form = node.text
            print(form, end=' ')
            # print([form], end=' ')
            print(transduce(form, decompose), end=' ')
            print(transduce(transduce(form, decompose), baptist), end=' ')
            print(transduce(transduce(form, decompose), chinese), end=' ')
            print()


if __name__ == '__main__':
    main()
