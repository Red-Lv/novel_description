#! /bin/env python
#! -*coding:GBK-*-

__author__ = 'lvleibing01'

import sys

import SuffixArraybyDC3


def binary_search(l, left, right, key):

    while left <= right:

        mid = (left + right) / 2

        if l[mid] <= key:
            left = mid + 1
        else:
            right = mid - 1

    return right


class LCS(object):

    def __init__(self):
        self.suffix_array = SuffixArraybyDC3.SuffixArraybyDC3()

        self.str_list = []
        self.sep = u'\u001a'
        self.start_index_list = []

    def init(self, *args):
        """
        """

        self.str_list = [list(_str) for _str in args]

        self.str_comp = self.sep.join(args)
        self.start_index_list.append(0)
        for _str in self.str_list:
            self.start_index_list.append(self.start_index_list[-1] + len(_str) + 1)
        self.start_index_list = self.start_index_list[: -1]

        self.suffix_array.init(self.str_comp)

        return True

    def exist_cs(self, k):
        """
        """

        str_cover_dict = {}
        cs_dict = {}
        cs_list = []
        for i in range(len(self.suffix_array.height_array)):

            if self.suffix_array.height_array[i] < k:
                str_cover_dict = {}
                continue

            pre_offset = self.suffix_array.SA[i - 1]
            offset = self.suffix_array.SA[i]

            str_index = binary_search(self.start_index_list, 0, len(self.start_index_list) - 1, pre_offset)
            str_cover_dict[str_index] = 1

            str_index = binary_search(self.start_index_list, 0, len(self.start_index_list) - 1, offset)
            str_cover_dict[str_index] = 1

            if len(str_cover_dict) >= len(self.str_list) * 0.2:
                cs = self.str_comp[self.suffix_array.SA[i]: ][: k]
                if cs.find(self.sep) == -1:
                    #print cs
                    cs_dict[cs] = 1

        return cs_dict.keys()

    def gen_lcs(self):
        """
        """

        self.suffix_array.gen_height_array()
        #self.suffix_array.dump_suffix_array()
        #self.suffix_array.dump_height_array()

        max_len = max(map(len, self.str_list))
        left, right = 1, max_len

        lcs = u''
        while left <= right:

            #print left, right
            mid = (left + right) / 2
            cs = self.exist_cs(mid)
            #print mid, cs
            if cs:
                lcs = cs
                left = mid + 1
            else:
                right = mid - 1
    
        cs_tot_list = []
        for i in range(right, 1, -1):
            cs_list = self.exist_cs(i)
            cs = []
            for item in cs_list:
                valid = True
                for cs_tot in cs_tot_list:
                    if cs_tot.find(item) != -1:
                        valid = False
                        break
                
                if valid: 
                    cs.append(item)

            cs_tot_list.extend(cs)
            
            print i
            print u'\u001a'.join(cs).encode('GBK', 'ignore')

        return True

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print 'Usage: __file__ file'.format(__file__)
        sys.exit(1)

    file = sys.argv[1]
    lcs = LCS()

    str_list = [unicode('我们的内容内容内容简介：', 'GBK'), unicode('武动乾坤内容简介：', 'GBK')]
    with open(file) as fp:

        str_list = []
        for line in fp:

            line = line.strip()
            if not line:
                continue

            str_list.append(unicode(line, 'GBK', 'ignore'))

    if not str_list:
        print 'str_list is empty'
        sys.exit(2)

    lcs.init(*str_list)
    lcs.gen_lcs()
