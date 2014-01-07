#! /bin/env python

import re
import sys
import json


def load_pattern(pattern_file):
    """
    """

    site_pattern_dict = {}
    try:
        with open(pattern_file) as fp:
            site_pattern_dict = json.load(fp, encoding='GBK')
    except Exception as e:
        site_pattern_dict = {}
        print 'fail to load pattern from file. err: {0}'.format(e)

    return site_pattern_dict


def fetch_pattern_group(pattern_info):
    """
    """

    mean_threshold = 1.0
    pattern_group_list = []
    pattern = pattern_info['pattern']
    offset_list = [m.start() for m in re.finditer(ur'\u0003', pattern)]

    for offset in offset_list:
        
        index = offset - 1
        while index >= max(offset - 4, 0):
            if pattern[index] == u'\u0003' or pattern[index] == u'\u0004':
                break
            index -= 1
        
        left = re.escape(pattern[index + 1: offset])
        if not left:
            if pattern_info['l_mean'] < mean_threshold:
                left = '^'

        index = offset + 1
        while index < min(offset + 5, len(pattern)):
            if pattern[index] == u'\u0003' or pattern[index] == u'\u0004':
                break
            index += 1
        
        right = re.escape(pattern[offset + 1: index])
        if not right:
            if pattern_info['r_mean'] < mean_threshold:
                right = '$'

        pattern_group_list.append((left, right))
    
    pattern_group_list = sorted(pattern_group_list, key=lambda item: min(map(len, item)), reverse=True)
    return pattern_group_list


cjk_punc_part_list = u'\u3008\u3009\u3010\u3011\u3014\u3015\u3016\u3017\u3018\u3019\u301a\u301b\u301d\u301e\u0022\u0022' \
                     u'\u0027\u0027\u0028\u0029\u003c\u003d\u005b\u005d\u007b\u007d'
cjk_punc_part_dict = {ch: index for index, ch in enumerate(cjk_punc_part_list)}


def fetch_seg_reverse(s, sentinel_regex=None):
    
    index = len(s) - 1
    while index >= 0:
        
        ch = s[index]
        if re.search(sentinel_regex, ch):
            break

        if ch in cjk_punc_part_dict:
            stop_index = fetch_seg_reverse(s[: index], re.escape(cjk_punc_part_list[cjk_punc_part_dict[ch] / 2 * 2 + 1 - cjk_punc_part_dict[ch] % 2]))
            index = stop_index

        index -= 1

    return index


def fetch_seg(s, sentinel_regex=None):
    
    index = 0
    while index < len(s):
        
        ch = s[index]
        if re.search(sentinel_regex, ch):
            break

        if ch in cjk_punc_part_dict:
            stop_index = fetch_seg(s[index + 1: ], re.escape(cjk_punc_part_list[cjk_punc_part_dict[ch] / 2 * 2 + 1 - cjk_punc_part_dict[ch] % 2]))
            index += stop_index + 1

        index += 1

    return index


def uni_str_filter(uni_str, regex=None):
    """
    """

    if not isinstance(uni_str, unicode):
        return u''

    if regex:
        return u''.join([m.group() for m in re.finditer(regex, uni_str)])
    else:
        return u''.join([m.group() for m in re.finditer(ur'[\u4e00-\u9fa5\w]+', uni_str)])


def pattern_employed(pattern_info_list, file):
    """
    """
    
    with open(file) as fp:
        for line in fp:

            line = unicode(line, 'GBK')
            line = line.strip('\n')
            if len(line.split(u'\t')) == 3:
                dir_id, _raw_book_name, _raw_pen_name = line.split(u'\t')
                dir_id, raw_book_name, raw_pen_name = line.split(u'\t')
                raw_book_name = uni_str_filter(raw_book_name)
                raw_pen_name = uni_str_filter(raw_pen_name)
                continue

            '''
            print '--------------'
            print line.encode('GBK')
            print '--------------'
            '''

            book_name = u''
            book_name_list = []
            for pattern_info in pattern_info_list:

                left, right = pattern_info

                assertion_list = []
                if left and left != '^':
                    assertion_list.append(left)
                if right and right != '$':
                    assertion_list.append(right)
                assertion = u'|'.join(assertion_list)

                regex = u'{0}(((?!{1}).)+){2}'.format(left, assertion, right)
                '''
                print '*********************'
                print regex.encode('GBK')
                print '*********************'
                '''

                m = re.search(regex, line)
                if not m:
                    continue
            
                s = m.group(1)
                book_name = s
                if not left:
                    
                    book_name = u''
                    index = 0
                    while index < len(s):

                        index += fetch_seg(s[::-1][index:], u'^(?![{0}])[^\u4e00-\u9fa5\w\u0003]'
                                                            u''.format(re.escape(cjk_punc_part_list)))
                        potential_book_name = uni_str_filter(s[::-1][: index][::-1], u'[\u4e00-\u9fa5\w\u0003\u0004]+')

                        if potential_book_name.find(raw_book_name) != -1:
                            book_name = s[::-1][: index][::-1]
                            break

                        index += 1

                if not right:

                    book_name = u''
                    index = 0
                    while index < len(s):

                        index += fetch_seg(s[index: ], u'^(?![{0}])[^\u4e00-\u9fa5\w\u0003]'
                                                       u''.format(re.escape(cjk_punc_part_list)))
                        potential_book_name = uni_str_filter(s[: index], u'[\u4e00-\u9fa5\w\u0003\u0004]+')

                        if potential_book_name.find(raw_book_name) != -1:
                            book_name = s[: index]
                            break

                        index += 1

                if len(uni_str_filter(book_name)) > 30 or uni_str_filter(book_name).find(raw_book_name) == -1:
                    book_name = u''

                if book_name:
                    book_name_list.append(book_name)
                    #break

            max_ratio = 0.0
            max_book_name = u''
            for book_name in book_name_list:

                book_name_filtered = uni_str_filter(book_name)
                ratio = len(raw_book_name) / float(len(book_name_filtered))
                if ratio > max_ratio and ratio > 1.0 / 3:
                    max_ratio = ratio
                    max_book_name = book_name

            book_name = max_book_name
            if not book_name and line.find(_raw_book_name) != -1:
                sys.stderr.write('{0}\t{1}\t{2}\n'.format(dir_id, _raw_book_name.encode('GBK', 'ignore'), _raw_pen_name.encode('GBK', 'ignore')))
                sys.stderr.write('{0}\n'.format(line.encode('GBK', 'ignore')))
                if _raw_book_name:
                    line = line.replace(_raw_book_name, u'\u0003')
                if _raw_pen_name:
                    line = line.replace(_raw_pen_name, u'\u0004')
                sys.stdout.write('{0}\n'.format(line.encode('GBK', 'ignore')))

            #print '\t'.join(['book_name: {0}'.format(book_name.encode('GBK')), str(len(uni_str_filter(book_name)))])
                       
if __name__ == '__main__':

    if len(sys.argv) != 4:
        print 'Usage: {9} pattern_file site_id site_desc_file'.format(__file__)
        sys.exit(1)

    pattern_file = sys.argv[1]
    site_id = sys.argv[2]
    site_desc_file = sys.argv[3]

    site_pattern_dict = load_pattern(pattern_file)

    print 'site_id: {0}'.format(site_id)

    pattern_info_list = site_pattern_dict.get(site_id)
    if not pattern_info_list:
        print 'site_id: {0} has no pattern'.format(site_id)
        sys.exit(2)

    pattern_group_list = []
    for pattern_info in pattern_info_list:
        pattern_group_list.extend(fetch_pattern_group(pattern_info))

    pattern_employed(pattern_group_list, site_desc_file)

    '''
    if len(sys.argv) != 3:

        for site_id in site_pattern_dict:

            print 'site_id: {0}'.format(site_id)

            pattern_info_list = site_pattern_dict.get(site_id)
            if not pattern_info_list:
                continue

            pattern_group_list = []
            for pattern_info in pattern_info_list:
                pattern_group_list.extend(fetch_pattern_group(pattern_info))

            pattern_employed(pattern_group_list, './data/{0}.txt.wf'.format(site_id))

    else:
        site_id = sys.argv[1]
        file = sys.argv[2]

        print 'site_id: {0}'.format(site_id)

        pattern_info_list = site_pattern_dict.get(site_id)
        if not pattern_info_list:
            sys.exit(1)

        pattern_group_list = []
        for pattern_info in pattern_info_list:
            pattern_group_list.extend(fetch_pattern_group(pattern_info))

        pattern_employed(pattern_group_list, file)
        '''
