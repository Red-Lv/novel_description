#! /bin/env python
#! -*coding:GBK-*-

__author__ = 'lvleibing01'


import re
import HTMLParser

from halfwidth_fullwidth_transformation.halfwidth_fullwidth_transformation import *


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
