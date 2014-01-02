#! /bin/env python
#! -*-coding:GBK-*-

__author__ = 'lvleibing01'

import re
import sys
import random
import HTMLParser

import MySQLdb


class HTMLParserExtended(HTMLParser.HTMLParser):
    
    def __init__(self):

        HTMLParser.HTMLParser.__init__(self)
        self.data = []
        
    def handle_data(self, data):

        self.data.append(data)
    
    def reset(self):

        HTMLParser.HTMLParser.reset(self)
        self.data = []


def sample_description(site_id, sample_size):

    try:
        conn = MySQLdb.connect(host='10.46.7.172', port=4195, user='wise_novelfmt_w', passwd='H4k3D8v9X2y5', db='novels')
        conn.set_character_set('GBK')
        conn.autocommit(True)
    except Exception as e:
        print 'fail to connect to the db fmt. error: {0}'.format(e)
        return 

    cursor = conn.cursor()

    query_sql = 'SELECT min(id), max(id) FROM dir_fmt_info{0}'.format(site_id)

    cursor.execute(query_sql)
    row = cursor.fetchone()

    if not row or not row[0]:
        cursor.close()
        conn.close()
        return
    
    min_id, max_id = row

    query_sql = 'SELECT raw_book_name, raw_pen_name, description FROM dir_fmt_info{0} WHERE id = %s'.format(site_id)

    hp_ex = HTMLParserExtended()

    valid_cnt = cnt = 0
    while valid_cnt < sample_size and cnt < sample_size * 2:

        cnt += 1

        id = random.randint(min_id, max_id)
        cursor.execute(query_sql, (id,))
        row = cursor.fetchone()

        if not row:
            continue

        row = map(lambda s: unicode(s.strip(), 'GBK', 'ignore'), row)
        raw_book_name, raw_pen_name, description = row

        sys.stderr.write('{0}\n'.format(description.encode('GBK', 'ignore')))

        if not description:
            continue

        while True:
            _data = data
            data = hp_ex.unescape(data)
            if _data == data:
                break

        hp_ex.reset()

        hp_ex.feed(data)

        data = u''.join(hp_ex.data)
        data = data.replace(u'\u00a0', u'\u0009')

        data = re.sub(u'\s+', u'\u0020', data)
        data = data.strip()

        if raw_book_name:
            data = data.replace(raw_book_name, u'\u0003')

        if raw_pen_name:
            data = data.replace(raw_book_name, u'\u0004')

        sys.stdout.write('{0}\n'.format(data.encode('GBK', 'ignore')))

        valid_cnt += 1
        
    cursor.close()
    conn.close()

if __name__ == '__main__':

    if len(sys.argv) != 2:

        print 'Usage: {0} site_id'.format(__file__)
        sys.exit(1)

    site_id = int(sys.argv[1])
    sample_size = 500

    sample_description(site_id, sample_size)
