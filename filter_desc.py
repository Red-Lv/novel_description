#! /bin/env python
#! -*coding:GBK-*-

__author__ = 'lvleibing01'

import re
import json

from util import *


class DescFilter(object):

    def __init__(self):

        pass

    def init(self, pattern_file):
        """
        """

        try:
            with open(pattern_file) as fp:
                self.site_desc_pattern = json.load(fp, encoding='GBK')
        except Exception as e:
            self.site_desc_pattern = {}
            print 'fail to load desc pattern from file. err: {0}'.format(e)

        self.valid_str_regex = re.compile(ur'[\u4e00-\u9fa5\w]')

        self.hp_ex = HTMLParserExtended()

        self.threshold = 3.0

        return True

    def filter_invalid_character(self, uni_str):
        """
        """

        uni_str_valid = u''
        for s in self.valid_str_regex.findall(uni_str):
            uni_str_valid += s

        return uni_str_valid

    def filter_desc(self, site_id, raw_book_name, raw_pen_name, raw_desc):
        """filter desc

        Arguments:
            raw_book_name:
            raw_pen_name:
            raw_desc:   description in unicode

        return:
            desc_filtered:  description filtered in unicode
        """

        book_name, pen_name, desc = map(html_element_filter, [raw_book_name, raw_pen_name, raw_desc])
        book_name_valid, pen_name_valid, desc_valid = map(self.filter_invalid_character, [book_name, pen_name, desc])

        desc_valid_replaced = desc_valid
        if book_name_valid:
            desc_valid_replaced = desc_valid_replaced.replace(book_name_valid, u'\u0003')
        if pen_name_valid:
            desc_valid_replaced = desc_valid_replaced.replace(pen_name_valid, u'\u0004')

        pattern_list = []
        if site_id in self.site_desc_pattern:
            pattern_list = self.site_desc_pattern[site_id]

        for pattern in pattern_list:

            regex = pattern['regex']
            type = pattern['type']
            mean = pattern['mean']
            std = pattern['std']

            m = re.search(regex, desc_valid_replaced, re.I)
            if not m:
                continue

            hit_part = m.group()
            offset = desc_valid_replaced.find(hit_part)
            l_wc, r_wc = offset, len(desc_valid_replaced) - offset - len(hit_part)
            wc = l_wc if type == 0 else r_wc

            if wc > mean + std * self.threshold:
                continue

            if type == 0:
                desc_valid_replaced = desc_valid_replaced[offset + len(hit_part): ]

            else:
                desc_valid_replaced = desc_valid_replaced[: offset]
