#! /bin/env python
#! -*-coding:GBK-*-

__author__ = 'lvleibing01'

import re
import sys
import numpy


def fetch_site_cs(cs_file):
    """
    """

    site_cs_dict = {}
    site_id = None
    with open(cs_file) as fp:
        for line in fp:
            
            line = line.strip()
            if not line:
                continue
            
            if line[:7] == 'site_id':
                site_id = int(line[line.find(':')+1:].strip())
                site_cs_dict[site_id] = []
                continue
            
            if re.match(r'\d+', line):
                continue
            
            line = unicode(line, 'GBK', 'ignore')
            line = line.split(u'\u001a')

            for cs in line:

                cs = cs.strip()
                if len(cs) < 2:
                    continue
                
                site_cs_dict[site_id].append(cs)
    
    return site_cs_dict


def fetch_cs_order(cs_list, desc_file):

    order_count_dict = {}
    with open(desc_file) as fp:
        for line in fp:
            
            line = line.strip()
            if not line:
                continue

            offset_list = []
            line = unicode(line, 'GBK', 'ignore')
            for i, cs in enumerate(cs_list):
                offset = line.find(cs)
                if offset != -1:
                    offset_list.append((i, offset))
            
            if len(offset_list) != len(cs_list):
                continue
            
            offset_list = sorted(offset_list, key=lambda item: item[1])

            key = u'\u001a'.join(map(lambda item: unicode(item[0]), offset_list))
            order_count_dict.setdefault(key, 0)
            order_count_dict[key] += 1
    
    max_key = u''
    max_count = 0
    for key, count in order_count_dict.items():
        if count > max_count:
            max_key = key
            max_count = count

    if max_key:
        cs_list_sorted = [cs_list[int(index)] for index in max_key.split(u'\u001a')] 
    else:
        cs_list_sorted = cs_list

    return cs_list_sorted


def filter_cs(cs, desc_file):
    """
    """

    wc_matrix = []
    with open(desc_file) as fp:
        for line in fp:
            
            line = line.strip()
            if not line:
                continue

            line = unicode(line, 'GBK', 'ignore')
            offset = line.find(cs)
            if offset == -1:
                continue

            l_wc, r_wc = offset, len(line) - offset - len(cs)
            wc_matrix.append((l_wc, r_wc))
    
    wc_matrix_trans = numpy.array(wc_matrix).transpose()
    cs_list = [cs, 'EOF']

    mean_threshold = 0.0
    std_threshold = 10.0

    if wc_matrix_trans.size and (numpy.std(wc_matrix_trans[0]) <= std_threshold or numpy.std(wc_matrix_trans[1]) <= std_threshold):

        print '-' * 20
        print 'mean:', numpy.mean(wc_matrix_trans[0])
        print 'std:', numpy.std(wc_matrix_trans[0])

        print cs.encode('GBK')

        print 'mean:', numpy.mean(wc_matrix_trans[1])
        print 'std:', numpy.std(wc_matrix_trans[1])

    return True

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print 'Usage: {0} cs_file desc_dir'.format(__file__)
        sys.exit(1)

    cs_file = sys.argv[1]
    desc_dir = sys.argv[2]

    site_cs_dict = fetch_site_cs(cs_file)
    for site_id in site_cs_dict:

        print 'site_id: {0}'.format(site_id)
        cs_list = site_cs_dict.get(site_id)
        if not cs_list:
            continue

        cs_list_sorted = fetch_cs_order(cs_list, './data/{0}.txt'.format(site_id))
        for value in cs_list_sorted:
            filter_cs(value, '{0}/{1}.txt'.format(desc_dir, site_id))

    '''
    site_cs_dict = fetch_site_cs('./result')

    if len(sys.argv) != 2:

        for site_id in site_cs_dict:

            cs_list = site_cs_dict.get(site_id)
            if not cs_list:
                continue

            cs_list_sorted = fetch_cs_order(cs_list, './data/{0}.txt'.format(site_id))
            for value in cs_list_sorted:
                filter_cs(value, './data/{0}.txt'.format(site_id))

    else:
        site_id = int(sys.argv[1])
        cs_list = site_cs_dict.get(site_id)

        if not cs_list:
            sys.exit(1)

        cs_list_sorted = fetch_cs_order(cs_list, './data/{0}.txt'.format(site_id))

        for value in cs_list_sorted:
            filter_cs(value, './data/{0}.txt'.format(site_id))
    '''
