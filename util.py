#! /bin/env python
#! -*coding:GBK-*-

__author__ = 'lvleibing01'


import HTMLParser


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

    data = uni_str
    hp_ex = HTMLParserExtended()

    while True:
        _data = data
        data = hp_ex.unescape(data)
        if _data == data:
            break

    hp_ex.feed(data)
    data = u''.join(hp_ex.data)

    data = data.replace(u'\u001a', u'\0020')

    return data
