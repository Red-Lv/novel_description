#!/usr/bin/env python
# -*- coding:GBK
# date: 2012/09/24 20:41
# mail: zhangjianrong@baidu.com
# author: zhangjianrong

import time
import os
import hashlib
import platform
from binascii import crc32


def fs64_sign(key):
    """
        fs64ǩ���㷨
    """
    os = platform.system()
    result = None
    if os == "Linux":
        import sign
        sign_result = sign.fs64(key)
        key1 = sign_result[1]
        key2 = sign_result[2]
        result = int(key1<<32) + key2
    elif os == "Windows":
        m = hashlib.md5()
        m.update(key)
        result = int(m.hexdigest(), 16) & 0xFFFFFFFFFFFFFFFF

    return result

def get_novel_cluster_table_id(book_name):
    """
        ����һ�����ڼ�Ⱥ�ϵı�ID
        Args:
            book_name:С˵��, unicode����
        Returns:
            table id
    """
    CLUSTER_TABLES_NUM = 256
    m = hashlib.md5()
    m.update(book_name.encode("GBK", "ignore"))
    table_id = int(m.hexdigest(), 16) % CLUSTER_TABLES_NUM

    return table_id


# ����gid�ĺ���
def get_novel_gid(book_name, pen_name):
    groupkey = "{0}@{1}".format(book_name, pen_name)
    return (crc32(groupkey) & 0xFFFFFFFF)

# ����book_id�ĺ���
def get_novel_book_id(book_name, pen_name, site):
    key = "{0}@{1}@{2}".format(book_name, pen_name, site)
    return (crc32(key) & 0xFFFFFFFF)


# ����ʱ���ļ�
def set_time_file(time_file, cur_time = -1):
    try:
        if cur_time == -1 :
            cur_time = int(time.time())
        f = open(time_file, "w")
        f.write("{0}\n".format(cur_time))
        f.close()
    except IOError as e:
        return 0

    return cur_time

def set_time_file_ex(time_file, cur_time):
    try:
        f = open(time_file, "w")
        f.write("{0}\n".format(cur_time))
        f.close()
    except IOError as e:
        return 0

    return cur_time

# ��ȡʱ���ļ�
def read_time_file(time_file):
    try:
        f = open(time_file, "r")
        line = f.readline()
        line = line.rstrip("\n ")
    except IOError as e:
        return -1

    if len(line) == 0:
        return -1

    return int(line)

# ����״̬�ļ�
def set_status_file(status_file):
    try:
        cur_time = int(time.time())
        f = open(status_file, "w")
        #f.write("{0}\n".format(cur_time))
        f.write("{0}\n".format(os.getpid()))#��¼pid
        f.close()
    except IOError as e:
        return False

    return True

# ɾ��״̬�ļ�
def remove_status_file(status_file):
    try:
        os.remove(status_file)
    except OSError as e:
        # û������ļ�
        return True

    return True

def get_site_from_url(dirurl, url_list = []):
    """
        ͨ��url�õ���Ӧ��վ��
    """
    sites = []
    for site in url_list:
        if dirurl.find(site) >= 0:
            sites.append(site)
    site_str_len = 0
    real_site = ''
    for site in sites:
        if len(site) > site_str_len:
            site_str_len = len(site)
            real_site = site

    return real_site


def chunk_list(l, n):
    """
        �ָ�list,ÿ����list�Ĵ�С������n
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def calc_align_id(chapter_title, pre_chapter_title = None):
    if pre_chapter_title:
        key = "{0}@{1}".format(pre_chapter_title, chapter_title)
        return fs64_sign(key)
    else:
        key = chapter_title
        return fs64_sign(key)


if __name__ == "__main__":
    key = 'http://www.fengwu.net/html/100/100609/10943538.html'
    print fs64_sign(key)



