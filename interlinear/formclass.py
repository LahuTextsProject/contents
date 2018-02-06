#
# -*- coding: utf-8 -*-

import re
import sys
import unicodecsv as csv
import codecs

def parse_form_class_file(filename):
    with open(filename, 'rt') as f:
        csvfile = csv.reader(f, delimiter='\t', encoding='utf-8')
        forms = {}
        for info in csvfile:
            key = str(info[0]).strip()
            annotation = info[1].strip()
            if len(info) == 3:
                output = str(info[2]).strip()
            else:
                output = re.sub(r'\.(.*)', r'\\textsubscript{\1}', info[0])
            forms[key] = [annotation, output]
        return forms
