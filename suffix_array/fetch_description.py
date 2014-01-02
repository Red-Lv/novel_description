#! /bin/env python
#! -*-coding:UTF-8-*-

import re
import sys
import random
import HTMLParser

import MySQLdb

class MyHTMLParser(HTMLParser.HTMLParser):
    
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.data = []
        
    def handle_data(self, data):
        self.data.append(data)
    
    def reset(self):
        HTMLParser.HTMLParser.reset(self)
        self.data = []

h = MyHTMLParser()

def fetch_description(site_id, count):

    try:
        conn = MySQLdb.connect(host='10.46.7.172', port=4195, user='wise_novelfmt_w', passwd='H4k3D8v9X2y5', db='novels')
    except Exception as e:
        print 'fail to connect to the db fmt. error: {0}'.format(e)
        return 

    cursor = conn.cursor()
    cursor.execute('SET NAMES GBK')
    cursor.execute('SET autocommit=1')

    query_sql = 'SELECT min(id), max(id) FROM dir_fmt_info{0}'.format(site_id)

    cursor.execute(query_sql)
    row = cursor.fetchone()

    if not row or not row[0]:
        cursor.close()
        conn.close()
        return
    
    min_id, max_id = row

    query_sql = 'SELECT raw_book_name, raw_pen_name, description FROM dir_fmt_info{0} WHERE id = %s'.format(site_id)

    i = 0
    tot = 0
    while i <= count and tot < count * 2:

        tot += 1

        id = random.randint(min_id, max_id)
        cursor.execute(query_sql, (id,))
        row = cursor.fetchone()

        if row:
            h.reset()
            '''
            tmp = list(row)
            tmp[2] = tmp[2].replace(tmp[0], u'\ufffe').replace(tmp[1], u'\uffff')
            row = tmp
            '''
            sys.stderr.write('{0}\n'.format(row[2]))

            if not row[2]:
                continue
                
            data = row[2].decode('GBK', 'ignore')
            data = data.replace(row[0].decode('GBK', 'ignore'), u'\u0003').replace(row[1].decode('GBK', 'ignore'), u'\u0004')
            #data = '&amp;lt;/span&amp;gt;'.decode('GBK', 'ignore')
            while True:
                _data = data
                data = h.unescape(data)
                if _data == data:
                    break
            
            data = re.sub(u'\s+', ' ', data)
            data = data.strip()

            h.feed(data)
            data = h.data
            data = u''.join(data)
            data = data.replace(u'\u00a0', u'\u0020')
            sys.stdout.write('{0}\n'.format(data.encode('GBK', 'ignore')))
        
            i += 1
        

    cursor.close()
    conn.close()

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print 'Usage: {0} site_id'.format(__file__)
        sys.exit(1)

    site_id = int(sys.argv[1])
    fetch_description(site_id, 500)
