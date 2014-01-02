#! /bin/env python
#! -*coding:GBK-*-

__author__ = 'lvleibing01'

import itertools


class SuffixArraybyDC3(object):

    def __init__(self):

        pass

    def init(self, s):

        self.s = s
        if isinstance(self.s, str):
            self.s = list(self.s)

        self.s = [ord(item) for item in s]
        self.K = max(self.s)

        self.SA = []
        self.RA = []
        self.h_array = []
        self.height_array = []

        return True

    def radix_sort(self, index_arr, ori_arr, K):
        """radix sort

        Arguments:
            index_arr:  subsequence of [0, 1, ... len(ori_arr)]
            ori_arr:    ori array
            K:  the element in ori_arr belongs to [0, K]
        """

        index_arr_len = len(index_arr)
        count = [0] * (K + 1)

        for i in xrange(index_arr_len):

            index = index_arr[i]
            count[ori_arr[index]] += 1

        _sum = 0
        for i in xrange(0, K + 1):
            count[i], _sum = _sum, count[i] + _sum

        index_arr_sorted = [0] * index_arr_len
        for i in range(index_arr_len):

            index = index_arr[i]

            index_arr_sorted[count[ori_arr[index]]] = index
            count[ori_arr[index]] += 1

        return index_arr_sorted

    def _gen_suffix_array(self, s, K):
        """
        """

        n = len(s)
        s.extend([0] * 3)

        #the count of element mod 3 == 0, 1, 2
        n0, n1, n2 = (n + 2) / 3, (n + 1) / 3, n / 3
        n02 = n0 + n2

        #index in [0, n) where position % 3 == 1
        #why n0 - n1:
        #   if (n - 1) % 3 == 0, the n % 3 == 1.
        #   so we need n in SA12 in the step 3: merging S0 with S12
        s12 = []
        for i in xrange(n + n0 - n1):
            if i % 3 != 0:
                s12.append(i)

        #sort the three element tuple starting at s12[0, 1, ... len(s12))
        SA12 = self.radix_sort(s12, s[2:], K)
        s12 = self.radix_sort(SA12, s[1:], K)
        SA12 = self.radix_sort(s12, s[0:], K)

        c0 = c1 = c2 = None
        count = 0
        for i in xrange(len(SA12)):

            index = SA12[i]
            if s[index] != c0 or s[index + 1] != c1 or s[index + 2] != c2:
                count += 1
                c0, c1, c2 = s[index: index + 3]

            if index % 3 == 1:
                s12[index / 3] = count
            else:
                #why n0 rather than n1?
                #   Because n0 is more significant than n1, for sometimes we need include n in the s12
                s12[index / 3 + n0] = count

        if count != len(s12):
            #recursive
            SA12 = self._gen_suffix_array(s12[:], count)
            #gen the s12 from SA12
            for i, index in enumerate(SA12):
                s12[index] = i + 1
        else:
            #gen the SA from s12
            for i, index in enumerate(s12):
                SA12[index - 1] = i

        #excellent idea. enjoy this
        s0 = [index * 3 for index in SA12 if index < n0]
        SA0 = self.radix_sort(s0, s, K)

        SA12 = map(lambda index: index * 3 + 1 if index < n0 else (index - n0) * 3 + 2, SA12)
        #why?
        #   pay attention to the step three: merging SA0 with SA12
        #   the None acts as a sentinel
        s12.append(0)

        SA = []
        #excellent trick
        i, j = 0,  n0 - n1
        while i < n0 and j < n02:

            def leq(t1, t2):

                for a, b in itertools.izip(t1, t2):
                    if a < b:
                        return True
                    if a > b:
                        return False

                return True

            index_0 = SA0[i]
            index_12 = SA12[j]

            if (leq((s[index_0], s12[index_0 / 3]),
                    (s[index_12], s12[n0 + index_12 / 3])) if index_12 % 3 == 1
                    else leq((s[index_0], s[index_0 + 1], s12[index_0 / 3 + n0]),
                             (s[index_12], s[index_12 + 1], s12[(index_12 + 2) / 3]))):

                SA.append(index_0)
                i += 1
            else:
                SA.append(index_12)
                j += 1
        else:

            if i < n0:
                SA.extend(SA0[i: n0])

            if j < n02:
                SA.extend(SA12[j: n02])

        return SA

    def gen_suffix_array(self):
        """
        """

        self.SA = self._gen_suffix_array(self.s[:], self.K)

    def gen_RA(self):
        """
        """

        if not self.SA:
            self.gen_suffix_array()

        self.RA = [0] * len(self.SA)
        for i, index in enumerate(self.SA):
            self.RA[index] = i

    def gen_h_array(self):
        """
        """

        if not self.RA:
            self.gen_RA()

        for i in xrange(len(self.s)):

            rank = self.RA[i]
            if not rank:
                self.h_array.append(0)
                continue

            start = self.h_array[i - 1] - 1 if i and self.h_array[i - 1] else 0
            _start_pre = self.SA[rank - 1] + start
            _start = i + start
            while _start_pre < len(self.s) and _start < len(self.s):
                if self.s[_start_pre] != self.s[_start]:
                    break

                start += 1
                _start_pre += 1
                _start += 1

            self.h_array.append(start)

    def gen_height_array(self):
        """
        """

        if not self.h_array:
            self.gen_h_array()

        self.height_array = [0] * len(self.h_array)
        for i, index in enumerate(self.SA):

            self.height_array[i] = self.h_array[index]

    def dump_suffix_array(self):
        """
        """

        for i in xrange(len(self.SA)):
            suffix = u''.join(map(unichr, self.s[self.SA[i]: ]))
            print u'\t'.join(map(unicode, [i, self.SA[i], suffix])).encode('GBK')

    def dump_h_array(self):
        """
        """

        for i in xrange(len(self.h_array)):
            print '\t'.join(map(str, [i, self.h_array[i]]))

    def dump_height_array(self):
        """
        """

        for i in xrange(len(self.height_array)):
            print '\t'.join(map(str, [i, self.height_array[i]]))

if __name__ == '__main__':

    suffix_array_dc3 = SuffixArraybyDC3()
    #suffix_array_dc3.init('xxxxyxxxzzxxxx', 128)
    suffix_array_dc3.init('abcefgafgbcdabcde')

    suffix_array_dc3.gen_suffix_array()

    suffix_array_dc3.dump_suffix_array()

    suffix_array_dc3.gen_height_array()

    #suffix_array_dc3.dump_h_array()

    suffix_array_dc3.dump_height_array()
