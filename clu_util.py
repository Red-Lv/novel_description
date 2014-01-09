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
        fs64签名算法
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
        计算一本书在集群上的表ID
        Args:
            book_name:小说名, unicode编码
        Returns:
            table id
    """
    CLUSTER_TABLES_NUM = 256
    m = hashlib.md5()
    m.update(book_name.encode("GBK", "ignore"))
    table_id = int(m.hexdigest(), 16) % CLUSTER_TABLES_NUM

    return table_id


# 计算gid的函数
def get_novel_gid(book_name, pen_name):
    groupkey = "{0}@{1}".format(book_name, pen_name)
    return (crc32(groupkey) & 0xFFFFFFFF)

# 计算book_id的函数
def get_novel_book_id(book_name, pen_name, site):
    key = "{0}@{1}@{2}".format(book_name, pen_name, site)
    return (crc32(key) & 0xFFFFFFFF)


# 设置时间文件
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

# 读取时间文件
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

# 设置状态文件
def set_status_file(status_file):
    try:
        cur_time = int(time.time())
        f = open(status_file, "w")
        #f.write("{0}\n".format(cur_time))
        f.write("{0}\n".format(os.getpid()))#记录pid
        f.close()
    except IOError as e:
        return False

    return True

# 删除状态文件
def remove_status_file(status_file):
    try:
        os.remove(status_file)
    except OSError as e:
        # 没有这个文件
        return True

    return True

def get_site_from_url(dirurl, url_list = []):
    """
        通过url得到对应的站点
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
        分割list,每个子list的大小不超过n
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



