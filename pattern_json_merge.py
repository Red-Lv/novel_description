#! /bin/env python
#! -*coding:GBK-*-

__author__ = 'lvleibing01'

import sys
import json


def merge_pattern(*args):
    """
    """

    pattern_merged = {}
    for pattern in args:
        for key, value in pattern.items():
            pattern_merged.setdefault(key, [])
            pattern_merged[key].extend(value)

    return pattern_merged

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print 'Usage: {0} pattern_files'.format(__file__)
        sys.exit(1)

    pattern_list = []
    for file in sys.argv[1:]:
        with open(file) as fp:
            pattern = json.load(fp, encoding='GBK')
            pattern_list.append(pattern)

    pattern_merged = merge_pattern(*pattern_list)

    json.dumps(pattern_merged, ensure_ascii=False, encoding='GBK')
