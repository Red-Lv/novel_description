#! /bin/env python
#! -*coding:GBK-*-

__author__ = 'lvleibing01'

import re
import json

from util import *
from book_name_pen_name_util import *


class DescFilter(object):

    def __init__(self):

        pass

    def init(self, book_name_pattern_file, pen_name_pattern_file, desc_pattern_file):
        """
        """

        self.book_name_pen_name_util = BookNamePenNameUtil()
        self.book_name_pen_name_util.init(book_name_pattern_file, pen_name_pattern_file)

        try:
            with open(desc_pattern_file) as fp:
                self.desc_pattern = json.load(fp, encoding='GBK')
        except Exception as e:
            self.desc_pattern = {}
            print 'fail to load desc pattern from file. err: {0}'.format(e)

        return True

    def filter_desc(self, site_id, raw_book_name, raw_pen_name, raw_desc):
        """
        """

        desc = html_element_filter(raw_desc)

        desc = self.book_name_pen_name_util.replace_book_name(site_id, raw_book_name, desc)
        desc = self.book_name_pen_name_util.replace_pen_name(site_id, raw_pen_name, desc)

        pattern_list = self.desc_pattern.get('{0}'.format(site_id), [])

        for pattern_info in pattern_list:

            pattern = pattern_info['pattern']
            type = pattern_info['type']
            l_mean = pattern_info['l_mean']
            l_std = pattern_info['l_std']
            r_mean = pattern_info['r_mean']
            r_std = pattern_info['r_std']

            offset = desc.find(pattern)
            if offset == -1:
                continue

            left, right = desc[: offset], desc[offset + len(pattern): ]
            desc = u''
            if type <= 0:
                if len(left) <= l_mean + l_std * 3.0:
                    desc += left

            if type >= 0:
                if len(right) <= r_mean + r_std * 3.0:
                    desc += right

        return desc

if __name__ == '__main__':

    desc_filter = DescFilter()
    desc_filter.init('./pattern/book_name_pattern.json', './pattern/pen_name_pattern.json', './pattern/desc_pattern.json')

    site_id =
    raw_book_name = u''
    raw_pen_name = u''
    raw_desc = u''

    desc = desc_filter.filter_desc(site_id, raw_book_name, raw_pen_name, raw_desc)
    print desc
