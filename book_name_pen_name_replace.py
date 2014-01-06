#! /bin/env python

import re
import sys
import json
from sets import *


def load_pattern(pattern_file):
    """
    """

    site_pattern_dict = {}
    with open(pattern_file) as fp:
        site_pattern_dict = json.load(fp, encoding='GBK')
    
    return site_pattern_dict

def filter_pattern(pattern_info):
    """
    """

    substr_list = []
    pattern = pattern_info['pattern']
    offset_list =  [m.start() for m in re.finditer(ur'\u0003', pattern)]
    
    for offset in offset_list:
        
        index = offset - 1
        while index >= max(offset - 4, 0):
            if pattern[index] == u'\u0003' or pattern[index] == u'\u0004':
                break
            index -= 1
        
        left = pattern[index + 1: offset]
        if not left:
            if pattern_info['l_mean'] < 1:
                left = '^'

        index = offset + 1
        while index < min(offset + 5, len(pattern)):
            if pattern[index] == u'\u0003' or pattern[index] == u'\u0004':
                break
            index += 1
        
        right = pattern[offset + 1: index]
        if not right:
            if pattern_info['r_mean'] < 1:
                right = '$'

        substr_list.append((left, right))
    
    substr_list = sorted(substr_list, key=lambda item: min(map(len, item)), reverse=True)
    return substr_list

cjk_punc_part_list = u'\u3008\u3009\u3010\u3011\u3014\u3015\u3016\u3017\u3018\u3019\u301a\u301b\u301d\u301e\u0022\u0022\u0027\u0027\u0028\u0029\u003c\u003d\u005b\u005d\u007b\u007d'
cjk_punc_part_dict = {ch: index for index, ch in enumerate(cjk_punc_part_list)}

def fetch_seg_reverse(s, sentinel_regex = u''):
    
    index = len(s) - 1
    while index >= 0:
        
        ch = s[index]
        #print sentinel_regex.encode('GBK')
        if re.search(sentinel_regex, ch):
            index -= 1
            break

        if ch in cjk_punc_part_dict:
            '''
            print ch
            print hex(ord(cjk_punc_part_list[cjk_punc_part_dict[ch] / 2 * 2 + 1 - cjk_punc_part_dict[ch] % 2]))
            '''
            stop_index = fetch_seg_reverse(s[: index], re.escape(cjk_punc_part_list[cjk_punc_part_dict[ch] / 2 * 2 + 1 - cjk_punc_part_dict[ch] % 2]))
            index = stop_index
            continue
        
        index -= 1

    return index

def fetch_seg(s, sentinel=None):
    
    index = 0
    while index < len(s):
        
        ch = s[index]
        if ch == sentinel:
            return index

        if ch in cjk_punc_part_dict:
            stop_index = fetch_seg(s[index + 1: ], cjk_punc_part_list[cjk_punc_part_dict[ch] / 2 * 2 + 1 - cjk_punc_part_dict[ch] % 2])
            index += stop_index + 1 
            index += 1
            continue
        
        if re.search(u'\u004e-\u9fa5\w\u0003', ch):
            index += 1
            continue
        
        break

    index -= 1
    return index
    
def pattern_employed(pattern_info_list, file):
    
   with open(file) as fp:
        for line in fp:

            line = unicode(line, 'GBK')
            if len(line.split(u'\t')) == 3:
                dir_id, raw_book_name, raw_pen_name = line.split(u'\t')
                raw_book_name_list = [m.group() for m in re.finditer(ur'[\u004e-\u9fa5\w\u0003\u0004]+', raw_book_name)]
                raw_book_name = u''.join(raw_book_name_list)
                continue

            print '--------------'
            print line.encode('GBK')
            print '--------------'

            book_name = u''
            for pattern_info in pattern_info_list:

                left, right = pattern_info
                regex = u'{0}(.+?){1}'.format(left, right)
                print '*********************'
                print regex.encode('GBK')
                print '*********************'

                m = re.search(regex, line)
                if not m:
                    continue
            
                s = m.group(1)
                print s.encode('GBK')
                book_name = s
                if not left:
                    
                    book_name =''
                    tmp = s
                    global_index = len(tmp)
                    while tmp:

                        index = fetch_seg_reverse(tmp, re.escape(u'^(?![{0}])[^\u004e-\u9fa5\w\u0003]'.format(cjk_punc_part_list)))
                        global_index -= len(tmp) - index
                        potential_book_name = u''.join([m.group() for m in re.finditer(ur'[\u004e-\u9fa5\w\u0003\u0004]+', s[global_index + 1: ])])

                        '''
                        print tmp.encode('GBK')
                        print len(tmp)
                        print index
                        print 'potential:', potential_book_name.encode('GBK')
                        print 'book_name:', book_name.encode('GBK')
                        '''

                        if Set(potential_book_name) & Set(raw_book_name):
                            book_name = s[global_index + 1: ]
                            break

                        tmp = tmp[: index - 1]
                    
                if not right:

                    book_name =''
                    tmp = s
                    cur_index = 0
                    while tmp:

                        index = fetch_seg(tmp)
                        cur_index += index
                        potential_book_name = u''.join([m.group() for m in re.finditer(ur'[\u004e-\u9fa5\w\u0003\u0004]+', s[: cur_index])])

                        '''
                        print tmp.encode('GBK')
                        print len(tmp)
                        print index
                        print 'potential:', potential_book_name.encode('GBK')
                        print 'book_name:', book_name.encode('GBK')
                        '''

                        if Set(potential_book_name) & Set(raw_book_name):
                            book_name = s[cur_index: ]
                            break

                       
                        if not potential_book_name:
                            index += 1
                        tmp = tmp[index + 1 : ]


                if len(book_name) > 20 or (not Set(book_name) & Set(raw_book_name)):
                    book_name = u''

                break

            print 'book_name:', book_name.encode('GBK')
                       
if __name__ == '__main__':

    site_pattern_dict = load_pattern('./book_name_pattern.json')

    if len(sys.argv) != 2:

        for site_id in site_pattern_dict:

            print 'site_id: {0}'.format(site_id)
            pattern_info_list = site_pattern_dict.get(site_id)
            if not pattern_info_list:
                continue

            pattern_info_filtered_list = []
            for pattern_info in pattern_info_list:
                pattern_info_filtered_list.extend(filter_pattern(pattern_info))

            pattern_employed(pattern_info_filtered_list, './data/{0}.txt.wf'.format(site_id))

    else:
        site_id = sys.argv[1]
        pattern_info_list = site_pattern_dict.get(site_id)
        if not pattern_info_list:
            sys.exit(1)
            
        pattern_info_filtered_list = []
        for pattern_info in pattern_info_list:
            pattern_info_filtered_list.extend(filter_pattern(pattern_info))

        pattern_employed(pattern_info_filtered_list, './data/{0}.txt.wf'.format(site_id))
