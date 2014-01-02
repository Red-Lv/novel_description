#! /bin/env python
#! -*coding:GBK-*-

__author__ = 'lvleibing01'

import sys

from suffix_array.SuffixArraybyDC3 import SuffixArraybyDC3


def binary_search(l, left, right, key):
    """
    """

    while left <= right:

        mid = (left + right) / 2

        if l[mid] <= key:
            left = mid + 1
        else:
            right = mid - 1

    return right


class LCS(object):

    def __init__(self):
        """
        """

        self.suffix_array = SuffixArraybyDC3()

        self.str_comp = u''
        self.sep = u'\u001a'

        self.seq_list = []
        self.start_offset_list = []

    def init(self, *args):
        """
        """

        self.seq_list = [list(s) for s in args]
        self.str_comp = self.sep.join(args)

        self.start_offset_list.append(0)
        for seq in self.seq_list:
            self.start_offset_list.append(self.start_offset_list[-1] + len(seq) + 1)

        self.start_offset_list = self.start_offset_list[: -1]

        self.suffix_array.init(self.str_comp)

        return True

    def check_cs_existence(self, k):
        """
        """

        potential_sa = []
        threshold = 0.2

        i = 0
        while i < len(self.suffix_array.height_array):

            if self.suffix_array.height_array[i] < k:
                i += 1
                continue

            j = i + 1
            while j < len(self.suffix_array.height_array):

                if self.suffix_array.height_array[j] < k:
                    break

                j += 1

            if j - i + 1 >= len(self.seq_list) * threshold:
                potential_sa.append((i, j))

            i = j + 1

        cs_dict = {}
        for i, j in potential_sa:

            str_cover_dict = {}
            for index in xrange(i, j):

                pre_offset = self.suffix_array.SA[index - 1]
                offset = self.suffix_array.SA[index]

                str_index = binary_search(self.start_offset_list, 0, len(self.start_offset_list) - 1, pre_offset)
                str_cover_dict[str_index] = 1

                str_index = binary_search(self.start_offset_list, 0, len(self.start_offset_list) - 1, offset)
                str_cover_dict[str_index] = 1

            if len(str_cover_dict) >= len(self.seq_list) * threshold:

                cs = self.str_comp[self.suffix_array.SA[i]: ][: k]
                if cs.find(self.sep) == -1:
                    cs_dict[cs] = 1

        return cs_dict.keys()

    def gen_lcs(self):
        """
        """

        self.suffix_array.gen_height_array()
        #self.suffix_array.dump_suffix_array()
        #self.suffix_array.dump_height_array()

        max_len = max(map(len, self.seq_list))
        left, right = 1, max_len

        while left <= right:

            mid = (left + right) / 2
            cs = self.check_cs_existence(mid)
            if cs:
                left = mid + 1
            else:
                right = mid - 1
    
        cs_list = []
        for i in range(right, 1, -1):

            i_cs_list = self.check_cs_existence(i)

            i_cs_valid_list = []
            for item in i_cs_list:

                valid = True
                for cs in cs_list:
                    if cs.find(item) != -1:
                        valid = False
                        break
                
                if valid: 
                    i_cs_valid_list.append(item)

            if not i_cs_valid_list:
                continue

            cs_list.extend(i_cs_valid_list)

            print i
            print u'\u001a'.join(i_cs_valid_list).encode('GBK', 'ignore')

        return True

if __name__ == '__main__':

    if len(sys.argv) != 2:

        print 'Usage: __file__ file'.format(__file__)
        sys.exit(1)

    file = sys.argv[1]
    lcs = LCS()

    seq_list = [unicode('我们的内容内容内容简介：', 'GBK', 'ignore'), unicode('武动乾坤内容简介：', 'GBK', 'ignore')]
    with open(file) as fp:

        seq_list = []
        for line in fp:

            line = line.strip()
            if not line:
                continue

            seq_list.append(unicode(line, 'GBK', 'ignore'))

    if not seq_list:
        print 'seq_list is empty'
        sys.exit(2)

    lcs.init(*seq_list)
    lcs.gen_lcs()
