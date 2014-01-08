#! /bin/env python
#! -*coding:UTF-8-*-

__author__ = 'lvleibing01'

import re
import sys
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

            pattern = pattern_info['pattern'].strip()
            type = int(pattern_info['type'])
            l_mean = float(pattern_info['l_mean'])
            l_std = float(pattern_info['l_std'])
            r_mean = float(pattern_info['r_mean'])
            r_std = float(pattern_info['r_std'])

            #print pattern.encode('GBK')
            offset = desc.find(pattern)
            if offset == -1:
                continue

            left, right = desc[: offset], desc[offset + len(pattern): ]
            desc = u''
            if type >= 0:
                desc += left

            if type <= 0:
                desc += right
            
            if re.search(ur'^[\u0003\u0004\s]+$', desc):
                desc = u''

        return desc

if __name__ == '__main__':
    
    '''
    if len(sys.argv) < 4:
        print 'Usage: {0} desc_pattern site_id desc_file'
        sys.exit(1)
    
    site_id = int(sys.argv[2])
    desc_file = sys.argv[3]
    '''
    desc_pattern_file = sys.argv[1]

    desc_filter = DescFilter()
    desc_filter.init('./pattern/book_name_pattern.json', './pattern/pen_name_pattern.json', desc_pattern_file)

    raw_book_name = u'\u0003'
    raw_pen_name = u'\u0004'

    '''
    with open(desc_file) as fp:
        for line in fp:
            
            line = line.strip('\n')
            if len(line.split('\t')) == 3:
                continue
            
            raw_desc = line.decode('GBK')
            desc = desc_filter.filter_desc(site_id, raw_book_name, raw_pen_name, raw_desc)

            if raw_desc == desc:
                sys.stderr.write('{0}\n'.format(desc.encode('GBK')))
            else:
                sys.stdout.write('------------------------------------\n')
                sys.stdout.write('{0}\n'.format(raw_desc.encode('GBK')))
                sys.stdout.write('{0}\n'.format(desc.encode('GBK')))
                sys.stdout.write('------------------------------------\n')
                '''
                
    site_id = 173
    raw_book_name = '爹地快追,妈咪快跑'.decode('UTF-8')
    raw_pen_name = '五月七日'.decode('UTF-8')
    raw_desc = '推荐: 《》 《》 《》 《》 《》'.decode('UTF-8')

    desc = desc_filter.filter_desc(site_id, raw_book_name, raw_pen_name, raw_desc)
    print desc.encode('GBK')
