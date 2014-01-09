#! /bin/env python
#! -*coding:GBK-*-

__author__ = 'lvleibing01'

import sys
import math

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

        if len(args) == 1:
            args += args

        self.seq_list = [list(s) for s in args]
        self.str_comp = self.sep.join(args)

        self.start_offset_list.append(0)
        for seq in self.seq_list:
            self.start_offset_list.append(self.start_offset_list[-1] + len(seq) + 1)

        self.start_offset_list = self.start_offset_list[: -1]

        self.suffix_array.init(self.str_comp)

        return True
    
    def cal_cs_threshold(self):
        """
        """

        #return math.floor((1 - (math.tanh(math.log(len(seq_list) / 100.0)) + 1) / 2.0 * 0.9) * len(seq_list))
        return len(self.seq_list)

    def check_cs_existence(self, k):
        """
        """

        potential_sa = []
        threshold = self.cal_cs_threshold()

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

            if j - i + 1 >= threshold:
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

            if len(str_cover_dict) >= threshold:

                cs = self.str_comp[self.suffix_array.SA[i]: ][: k]
                if cs.find(self.sep) == -1:
                    return cs

        return u''

    def gen_lcs(self):
        """
        """

        self.suffix_array.gen_height_array()
        #self.suffix_array.dump_suffix_array()
        #self.suffix_array.dump_height_array()

        max_len = max(map(len, self.seq_list))
        left, right = 1, max_len
        lcs = u''

        while left <= right:

            mid = (left + right) / 2
            cs = self.check_cs_existence(mid)
            if cs:
                left = mid + 1
                lcs = cs
            else:
                right = mid - 1

        return lcs


if __name__ == '__main__':

    lcs = LCS()

    seq_list = [unicode('我们的内容内容内容简介：', 'GBK', 'ignore'),unicode('我们的内容内容内容简介：', 'GBK', 'ignore')]
    if not seq_list:
        print 'seq_list is empty'
        sys.exit(2)

    lcs.init(*seq_list)
    result = lcs.gen_lcs()
    print result.encode('GBK')
