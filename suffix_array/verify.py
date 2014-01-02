#! /bin/env python
#! -*-coding:GBK-*-

import re
import sys
import numpy

def fetch_site_cs(file):
    """
    """

    site_cs_dict = {}
    site_id = None
    with open(file) as fp:
        for line in fp:
            
            line = line.strip()
            if not line:
                continue
            
            if line[:7] == 'site_id':
                site_id = int(line[line.find('.')+1:])
                site_cs_dict[site_id] = []
                continue
            
            if re.match(r'\d+', line):
                continue
            
            line = unicode(line, 'GBK')
            line = line.split(u'\u001a')
            for item in line:

                item = item.strip()
                if len(item) < 2:
                    continue
                
                site_cs_dict[site_id].append(item)
    
    return site_cs_dict

def fetch_cs_order(cs_list, file):

    count = {}
    with open(file) as fp:
        for line in fp:
            
            line = line.strip()
            if not line:
                continue

            offset_list = []
            #print line
            line = unicode(line, 'GBK')
            for i, cs in enumerate(cs_list):
                if line.find(cs) != -1:
                    offset_list.append((i, line.find(cs)))
            
            if len(offset_list) != len(cs_list):
                continue
            
            offset_list = sorted(offset_list, key=lambda item: item[1])
            key = u'\u001a'.join(map(unicode, [index for index, offset in offset_list]))
            count.setdefault(key, 0)
            count[key] += 1
    
    max_key = None
    max_count = 0
    for key, count in count.items():
        if count > max_count:
            max_key = key
            max_count = count

    if max_key:
        cs_list_sorted = [cs_list[int(index)] for index in max_key.split(u'\u001a')] 
    else:
        cs_list_sorted = cs_list

    return cs_list_sorted
 
def process_site_description(cs, file):

    w_list = []
    with open(file) as fp:
        for line in fp:
            
            line = line.strip()
            if not line:
                continue

            line = unicode(line, 'GBK')
            wordcount = []
            offset = line.find(cs) 
            if offset == -1:
                continue

            wordcount.append((offset, len(line) - offset - len(cs)))
            w_list.append(wordcount)
    
    '''
    for item in w_list:
        print item
        '''

    w_trans = numpy.array(w_list).transpose()
    cs_list_sorted = [cs, 'EOF']
    for _cs, w in zip(cs_list_sorted, w_trans):
        print  'mean',numpy.mean(w) 
        print  'std',numpy.std(w) 
        print _cs.encode('GBK')

    return True

if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print 'Usage: {0} site_id'.format(__file__)
        sys.exit(1)

    site_cs_dict = fetch_site_cs('./result.new.new')
    site_id = int(sys.argv[1])
    if not site_cs_dict.get(site_id):
        sys.exit(2)
    cs_list_sorted = fetch_cs_order(site_cs_dict[site_id], './data/{0}.txt'.format(site_id))

    for value in cs_list_sorted: 
        print '----------------------------------'
        process_site_description(value, './data/{0}.txt'.format(site_id))
