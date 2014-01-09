#! /bin/env python
#! -*coding:GBK-*-

__author__ = 'lvleibing01'


import re
import HTMLParser

from halfwidth_fullwidth_transformation.halfwidth_fullwidth_transformation import *
from dataframe_util import *

#prefix_punc_str = '〈《「『〔〖??([{'
prefix_punc_str = u'\u3008\u300a\u300c\u300d\u3010\u3014\u3016\u3018\u301a\u0028\u005b\u007b'
#suffix_punc_str = 〉》」』〕〗??)]}'
suffix_punc_str = u'\u3009\u300b\u300d\u300f\u3011\u3015\u3017\u3019\u301b\u0029\u005d\u007d'

prefix_punc_dict = {prefix_punc: index for index, prefix_punc in enumerate(prefix_punc_str)}
suffix_punc_dict = {suffix_punc: index for index, suffix_punc in enumerate(suffix_punc_str)}

class HTMLParserExtended(HTMLParser.HTMLParser):

    def __init__(self):

        HTMLParser.HTMLParser.__init__(self)
        self.data = []

    def handle_data(self, data):

        self.data.append(data)

    def reset(self):

        HTMLParser.HTMLParser.reset(self)
        self.data = []


def html_element_filter(uni_str):

    data = u''.join([fullwidth_to_halfwidth(uni_chr) for uni_chr in uni_str])

    hp_ex = HTMLParserExtended()

    while True:
        _data = data
        data = hp_ex.unescape(data)
        if _data == data:
            break

    hp_ex.feed(data)
    data = u''.join(hp_ex.data)

    data = data.replace(u'\u00a0', u'\0020')
    data = re.sub(u'\s+', u'\u0020', data)
    data = data.strip()

    return data
