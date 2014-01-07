#! /bin/env python

import re
import json


class BookNamePenNameUtil(object):

    def __init__(self):

        self.book_name_char = u'\u0003'
        self.pen_name_char = u'\u0004'

        self.cjk_punc_part_list = u'\u3008\u3009\u3010\u3011\u3014\u3015\u3016\u3017\u3018\u3019\u301a\u301b\u301d' \
                                  u'\u301e\u0022\u0022\u0027\u0027\u0028\u0029\u003c\u003d\u005b\u005d\u007b\u007d'
        self.cjk_punc_part_dict = {ch: index for index, ch in enumerate(self.cjk_punc_part_list)}

    def init(self, book_name_pattern_file, pen_name_pattern_file):
        """
        """

        book_name_pattern = self.load_pattern(book_name_pattern_file)
        pen_name_pattern = self.load_pattern(pen_name_pattern_file)

        self.book_name_pattern_group_list = {}
        for site_id in book_name_pattern:

            self.book_name_pattern_group_list.setdefault(site_id, [])
            for pattern_info in book_name_pattern[site_id]:
                self.book_name_pattern_group_list[site_id].append(self.fetch_pattern_group(self.book_name_char, pattern_info))

        self.pen_name_pattern_group_list = {}
        for site_id in pen_name_pattern:

            self.pen_name_pattern_group_list.setdefault(site_id, [])
            for pattern_info in pen_name_pattern[site_id]:
                self.pen_name_pattern_group_list[site_id].append(self.fetch_pattern_group(self.pen_name_char, pattern_info))

        return True

    def load_pattern(self, pattern_file):
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

    def fetch_pattern_group(self, sep, pattern_info):
        """
        """

        mean_threshold = 1.0
        pattern_group_list = []
        pattern = pattern_info['pattern']
        offset_list = [m.start() for m in re.finditer(sep, pattern)]

        for offset in offset_list:
        
            index = offset - 1
            while index >= max(offset - 4, 0):
                if pattern[index] == self.book_name_char or pattern[index] == self.pen_name_char:
                    break
                index -= 1
        
            left = re.escape(pattern[index + 1: offset])
            if not left:
                if pattern_info['l_mean'] < mean_threshold:
                    left = '^'

            index = offset + 1
            while index < min(offset + 5, len(pattern)):
                if pattern[index] == self.book_name_char or pattern[index] == self.pen_name_char:
                    break
                index += 1
        
            right = re.escape(pattern[offset + 1: index])
            if not right:
                if pattern_info['r_mean'] < mean_threshold:
                    right = '$'

            pattern_group_list.append((left, right))
    
        pattern_group_list = sorted(pattern_group_list, key=lambda item: min(map(len, item)), reverse=True)
        return pattern_group_list

    def fetch_seg(self, s, sentinel_regex=None):
    
        index = 0
        while index < len(s):
        
            ch = s[index]
            if re.search(sentinel_regex, ch):
                break

            if ch in self.cjk_punc_part_dict:
                stop_index = self.fetch_seg(s[index + 1: ],
                                            re.escape(self.cjk_punc_part_list[self.cjk_punc_part_dict[ch] / 2 * 2 + 1 -
                                                                              self.cjk_punc_part_dict[ch] % 2]))
                index += stop_index + 1

            index += 1

        return index


    def uni_str_filter(self, uni_str, regex=None):
        """
        """

        if not isinstance(uni_str, unicode):
            return u''

        if regex:
            return u''.join([m.group() for m in re.finditer(regex, uni_str)])
        else:
            return u''.join([m.group() for m in re.finditer(ur'[\u4e00-\u9fa5\w]+', uni_str)])

    def replace_book_name(self, site_id, raw_book_name, raw_desc):
        """
        """

        _raw_book_name = raw_book_name
        raw_book_name = self.uni_str_filter(_raw_book_name)

        pattern_group_list = self.book_name_pattern_group_list.get('{0}'.format(site_id), [])

        book_name_list = []
        for pattern_group in pattern_group_list:

            left, right = pattern_group

            assertion_list = []
            if left and left != '^':
                assertion_list.append(left)
            if right and right != '$':
                assertion_list.append(right)
            assertion = u'|'.join(assertion_list)

            regex = u'{0}(((?!{1}).)+){2}'.format(left, assertion, right)

            m = re.search(regex, raw_desc)
            if not m:
                continue
            
            s = m.group(1)
            book_name = s
            if not left:
                    
                book_name = u''
                index = 0
                while index < len(s):

                    index += self.fetch_seg(s[::-1][index:], u'^(?![{0}])[^\u4e00-\u9fa5\w\u0003]'
                                                             u''.format(re.escape(self.cjk_punc_part_list)))
                    potential_book_name = self.uni_str_filter(s[::-1][: index][::-1], u'[\u4e00-\u9fa5\w\u0003\u0004]+')

                    if potential_book_name.find(raw_book_name) != -1:
                        book_name = s[::-1][: index][::-1]
                        break

                    index += 1

            if not right:

                book_name = u''
                index = 0
                while index < len(s):

                    index += self.fetch_seg(s[index: ], u'^(?![{0}])[^\u4e00-\u9fa5\w\u0003]'
                                                       u''.format(re.escape(self.cjk_punc_part_list)))
                    potential_book_name = self.uni_str_filter(s[: index], u'[\u4e00-\u9fa5\w\u0003\u0004]+')

                    if potential_book_name.find(raw_book_name) != -1:
                        book_name = s[: index]
                        break

                    index += 1

            if len(self.uni_str_filter(book_name)) > 30 or self.uni_str_filter(book_name).find(raw_book_name) == -1:
                book_name = u''

            if book_name:
                book_name_list.append(book_name)
                #break

        max_ratio = 0.0
        max_book_name = u''
        for book_name in book_name_list:

            book_name_filtered = self.uni_str_filter(book_name)
            ratio = len(raw_book_name) / float(len(book_name_filtered))
            if ratio > max_ratio and ratio > 1.0 / 3:
                max_ratio = ratio
                max_book_name = book_name

        book_name = max_book_name
        if not book_name:
            book_name = _raw_book_name

        if book_name:
            raw_desc = raw_desc.replace(book_name, self.book_name_char)

        return raw_desc

    def replace_pen_name(self, site_id, raw_pen_name, raw_desc):
        """
        """

        _raw_pen_name = raw_pen_name
        raw_pen_name = self.uni_str_filter(_raw_pen_name)

        pattern_group_list = self.pen_name_pattern_group_list.get('{0}'.format(site_id), [])

        pen_name_list = []
        for pattern_group in pattern_group_list:

            left, right = pattern_group

            assertion_list = []
            if left and left != '^':
                assertion_list.append(left)
            if right and right != '$':
                assertion_list.append(right)
            assertion = u'|'.join(assertion_list)

            regex = u'{0}(((?!{1}).)+){2}'.format(left, assertion, right)

            m = re.search(regex, raw_desc)
            if not m:
                continue

            s = m.group(1)
            pen_name = s
            if not left:

                pen_name = u''
                index = 0
                while index < len(s):

                    index += self.fetch_seg(s[::-1][index:], u'^(?![{0}])[^\u4e00-\u9fa5\w\u0004]'
                                                             u''.format(re.escape(self.cjk_punc_part_list)))
                    potential_pen_name = self.uni_str_filter(s[::-1][: index][::-1], u'[\u4e00-\u9fa5\w\u0003\u0004]+')

                    if potential_pen_name.find(raw_pen_name) != -1:
                        pen_name = s[::-1][: index][::-1]
                        break

                    index += 1

            if not right:

                pen_name = u''
                index = 0
                while index < len(s):

                    index += self.fetch_seg(s[index: ], u'^(?![{0}])[^\u4e00-\u9fa5\w\u0004]'
                                                        u''.format(re.escape(self.cjk_punc_part_list)))
                    potential_pen_name = self.uni_str_filter(s[: index], u'[\u4e00-\u9fa5\w\u0003\u0004]+')

                    if potential_pen_name.find(raw_pen_name) != -1:
                        pen_name = s[: index]
                        break

                    index += 1

            if len(self.uni_str_filter(pen_name)) > 30 or self.uni_str_filter(pen_name).find(raw_pen_name) == -1:
                pen_name = u''

            if pen_name:
                pen_name_list.append(pen_name)
                #break

        max_ratio = 0.0
        max_pen_name = u''
        for pen_name in pen_name_list:

            pen_name_filtered = self.uni_str_filter(pen_name)
            ratio = len(raw_pen_name) / float(len(pen_name_filtered))
            if ratio > max_ratio and ratio > 1.0 / 3:
                max_ratio = ratio
                max_pen_name = pen_name

        pen_name = max_pen_name
        if not pen_name:
            pen_name = _raw_pen_name

        if pen_name:
            raw_desc = raw_desc.replace(pen_name, self.pen_name_char)

        return raw_desc

if __name__ == '__main__':

    book_name_pen_name_util = BookNamePenNameUtil()
