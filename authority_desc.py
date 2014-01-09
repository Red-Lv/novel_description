#! /bin/env python
# -*-coding:GBK-*-

__author__ = 'lvleibing01'

import sys
import random

import MySQLdb

from util import *
from LCS import *

import filter_desc


class AuthorityDesc(object):

    def __init__(self):

        pass

    def init(self, rid_list):

        self.rid_list = random.sample(rid_list, 200 if len(rid_list) > 200 else len(rid_list))
        self.desc_filter = filter_desc.DescFilter()
        self.desc_filter.init('./pattern/book_name_pattern.json', './pattern/pen_name_pattern.json',
                              './pattern/desc_pattern.json')

        self.lcs = LCS()

        return True

    def __del__(self):

        pass

    def exit(self):

        return True

    def run(self):

        self.process()

        return True

    def process(self):

        print 'start processing'

        authority_info_list = self.fetch_authority_info()

        authority_info_len = len(authority_info_list)
        authority_info_index = 0

        for rid, book_name, pen_name, book_desc in authority_info_list:

            print 'index: {0}. tot: {1}'.format(authority_info_index, authority_info_len)
            authority_info_index += 1

            book_desc_update = self.check_authority_desc(book_name, pen_name, rid)

        print 'finish processing'

        return True

    def fetch_authority_info(self):

        print 'start fetching authority info'

        authority_info_list = []

        try:
            conn = MySQLdb.connect(host='10.46.7.171', port=4198, user='wise_novelclu_w', passwd='C9l3U4n6M2e1',
                                   db='novels_new')
            conn.set_character_set('GBK')
            conn.autocommit(True)
        except Exception as e:
            print 'fail to connect to the cluster db. error: {0}'.format(e)
            return authority_info_list

        cursor = conn.cursor()

        query_sql = 'SELECT rid, book_name, pen_name, description FROM novel_authority_info ' \
                    'WHERE rid = %s AND rank > 0'.format()
    
        for rid in self.rid_list:

            cursor.execute(query_sql, (rid,))
            row = cursor.fetchone()

            if not row:
                continue

            authority_info_list.append(row)

        cursor.close()
        conn.close()

        print 'finish fetching authority info. no: {0}'.format(len(authority_info_list))

        return authority_info_list

    def check_authority_desc(self, book_name, pen_name, rid):
        """
        """

        authority_desc = ''
        cluster_info = self.fetch_cluster_info(book_name, rid)
        cluster_info = sorted(cluster_info, key=lambda item: item[-1], reverse=True)

        if not cluster_info:
            return authority_desc

        native_desc_list = []
        for site_id, dir_id, dir_url, rank in cluster_info:

            row = self.fetch_native_desc(site_id, dir_id)
            if not row:
                continue

            raw_book_name, raw_pen_name, raw_desc = self.fetch_native_desc(site_id, dir_id)

            native_desc = self.desc_filter.filter_desc(site_id, *map(lambda uni_str: unicode(uni_str, 'GBK', 'ignore'),
                                                                     [raw_book_name, raw_pen_name, raw_desc]))
            if not self.is_valid_desc(native_desc):
                continue

            print '-' * 20
            print 'site_id: {0}'.format(site_id)
            print 'dir_id: {0}'.format(dir_id)
            print 'dir_url: {0}'.format(dir_url)
            #print 'raw_desc: {0}'.format(raw_desc)
            print 'native_desc: {0}'.format(native_desc.encode('GBK', 'ignore'))

            native_desc_list.append(native_desc)

        authority_desc = self.authority_desc_strategy(native_desc_list)
        authority_desc = authority_desc.replace(u'\u0003', unicode(book_name, 'GBK'))
        authority_desc = authority_desc.replace(u'\u0004', unicode(pen_name, 'GBK'))
        authority_desc = authority_desc.encode('GBK', 'ignore')

        dir_url = cluster_info[0][2]
        print '*' * 20
        print '\t'.join(map(str, [rid, book_name, pen_name, dir_url, authority_desc]))

        return authority_desc

    def is_valid_desc(self, desc):
        """
        """

        valid_desc_len_threshold = 1
        desc_filtered = re.sub(u'[^\u4e00-\u9fa5\w]', '', desc)

        return len(desc_filtered) >= valid_desc_len_threshold

    def authority_desc_strategy(self, native_desc_list):
        """
        """

        authority_desc = ''

        if not native_desc_list:
            return authority_desc

        native_desc_filtered_list = [re.sub(u'[^\u4e00-\u9fa5\w\s]', u'\u001a', native_desc)
                                     for native_desc in native_desc_list]

        key_sent_list = []
        key_sent_dict = {}
        group_elem_dict = {}
        for i, native_desc in enumerate(native_desc_filtered_list):

            key_sent = self.extract_key_sent(native_desc, u'\u001a')
            if not key_sent:
                continue

            key_sent_list.append(key_sent)

            group_index = key_sent_dict.get(key_sent, len(key_sent_dict))
            key_sent_dict.setdefault(key_sent, group_index)
            group_elem_dict.setdefault(group_index, set())
            group_elem_dict[group_index].add(i)

        native_desc_filtered_list = [re.sub(u'\s+', '', native_desc.replace(u'\u001a', u''))
                                     for native_desc in native_desc_filtered_list]
        group_lcs_dict = {}
        for group_index in group_elem_dict:

            self.lcs.init(*[native_desc_filtered_list[i] for i in group_elem_dict[group_index]])
            lcs = self.lcs.gen_lcs()
            group_lcs_dict[group_index] = lcs

        Jaccard_index_extend_threshold = 0.8
        for i in xrange(len(group_lcs_dict)):
            for j in xrange(i + 1, len(group_lcs_dict)):
                if not group_lcs_dict[j]:
                    continue

                self.lcs.init(group_lcs_dict[i], group_lcs_dict[j])
                lcs = self.lcs.gen_lcs()

                Jaccard_index_extend = len(lcs) / float(min(len(group_lcs_dict[i]), len(group_lcs_dict[j])))
                if Jaccard_index_extend >= Jaccard_index_extend_threshold:
                    group_elem_dict[i] |= group_elem_dict[j]
                    group_elem_dict[j] = set()

        max_score = 0
        max_group_index = -1
        for group_index in group_elem_dict:

            def calc_group_score(elem_set):
                return sum(map(lambda index: len(native_desc_filtered_list) - index, elem_set))

            group_score = calc_group_score(group_elem_dict[group_index])
            if group_score > max_score:
                max_score = group_score
                max_group_index = group_index

        potential_group= sorted(group_elem_dict[max_group_index], key=lambda index: len(native_desc_filtered_list[index]))
        authority_desc = native_desc_list[potential_group[(len(potential_group) - 1) / 2]]

        return authority_desc

    def extract_key_sent(self, uni_str, sep):
        """
        """

        if not isinstance(uni_str, unicode):
            print 'uni_str is not an instance of unicode'

        key_sent = u''
        for sent in uni_str.split(sep):
            if len(sent) > len(key_sent):
                key_sent = sent

        return key_sent

    def fetch_cluster_info(self, book_name, rid):
        """
        """

        cluster_info = []

        try:
            conn = MySQLdb.connect(host='10.46.7.171', port=4198, user='wise_novelclu_w', passwd='C9l3U4n6M2e1', db='novels_new')
            conn.set_character_set('GBK')
            conn.autocommit(True)
        except Exception as e:
            print 'fail to connect to the cluster db. error: {0}'.format(e)
            return cluster_info

        cluster_table_id = get_novel_cluster_table_id(book_name.decode('GBK', 'ignore'))

        query_sql = 'SELECT site_id, dir_id, dir_url, rank FROM novel_cluster_info{0} WHERE cluster_id = {1}' \
                    ''.format(cluster_table_id, rid)

        cursor = conn.cursor()

        cursor.execute(query_sql)
        rows = cursor.fetchall()
        cluster_info = rows

        cursor.close()
        conn.close()

        return cluster_info

    def fetch_native_desc(self, site_id, dir_id):
        """
        """

        native_desc = ''

        try:
            conn = MySQLdb.connect(host='10.46.7.172', port=4195, user='wise_novelfmt_w', passwd='H4k3D8v9X2y5', db='novels')
        except Exception as e:
            print 'fail to connect to the db format. error: {0}'.format(e)
            return native_desc

        query_sql = 'SELECT raw_book_name, raw_pen_name, description FROM dir_fmt_info{0} WHERE dir_id = {1}'.format(site_id, dir_id)

        cursor = conn.cursor()
        cursor.execute('SET NAMES GBK')
        cursor.execute('SET autocommit=1')

        cursor.execute(query_sql)
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        return row

    def update_authority_info(self, authority_info_list):

        print 'start updating authority info. no: {0}'.format(len(authority_info_list))

        try:
            conn = MySQLdb.connect(host='10.46.7.171', port=4198, user='wise_novelclu_w', passwd='C9l3U4n6M2e1', db='novels_new')
        except Exception as e:
            print 'fail to connect to the cluster db. error: {0}'.format(e)
            return False

        update_sql = 'UPDATE novel_authority_info SET book_desc = %s WHERE rid = %s'

        cursor = conn.cursor()
        cursor.execute('SET NAMES GBK')
        cursor.execute('SET autocommit=1')

        for book_name, rid, book_desc in authority_info_list:

            cursor.execute(update_sql, (book_desc, rid))

        cursor.close()
        conn.close()

        print 'finish updating authority info'

        return True

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print 'Usage: {0} rid_file'.format(__file__)
        sys.exit(1)
    
    rid_file = sys.argv[1]
    rid_list = []
    with open(rid_file) as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            rid_list.append(int(line))
    authority_desc = AuthorityDesc()
    authority_desc.init(rid_list)

    authority_desc.run()

    authority_desc.exit()
