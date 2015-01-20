#!usr/bin/env python

import sys,os,codecs
import xml.etree.ElementTree as ET
from Transducer import transduce,chinese,baptist,decompose

def main():
#  for line in open('lahu_writing.txt','rU'):
#    for word in line.split():
#      print word,
#      print transduce(word,decompose),
#      print transduce(transduce(word,decompose),chinese),
#      print transduce(transduce(word,decompose),baptist)

  f = open('4testLahuTexts.xml','rt')
  tree = ET.parse(f)
  f.close()
  for node in tree.findall('.//word/words/word/item'):
    if node.attrib['type'] == 'txt':
      form = codecs.encode(node.text,'utf8')
      print form,
      print [form],
      print transduce(form,decompose),
      print transduce(transduce(form,decompose),chinese),
      print transduce(transduce(form,decompose),baptist)


if __name__ == '__main__':
  main()
