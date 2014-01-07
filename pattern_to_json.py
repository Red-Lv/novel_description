#! /bin/env python

import re
import sys
import json
import math


def trans_pattern_to_json(pattern_file):
    """
    """

    site_pattern_dict = {}
    site_id = None
    with open(pattern_file) as fp:
        for line in fp:
            
            line = line.strip('\n')
            if not line:
                continue
            
            if line[: 7] == 'site_id':
                site_id = int(line[line.find(':') + 1: ].strip())
                site_pattern_dict[site_id] = []
                continue
            
            if re.match(r'^\d+$', line):
                continue
           
            if re.match(r'-+', line):
                pattern_info = {}
                continue
            
            if re.match(r'mean:', line):
                if 'pattern' not in pattern_info: 
                    pattern_info['l_mean'] = float(line.split(':')[1].strip())
                else:                    
                    pattern_info['r_mean'] = float(line.split(':')[1].strip())

            elif re.match(r'std:', line):
                pattern_info.setdefault('type', 0)
                if 'pattern' not in pattern_info: 
                    pattern_info['l_std'] = float(line.split(':')[1].strip())
                    if pattern_info['l_std'] <= 10:
                        pattern_info['type'] += -1
                else:                    
                    pattern_info['r_std'] = float(line.split(':')[1].strip())
                    if pattern_info['r_std'] <= 10:
                        pattern_info['type'] += 1

            else: 
                pattern_info['pattern'] = line
            
            if len(pattern_info) == 6:
                site_pattern_dict[site_id].append(pattern_info)
        
        print json.dumps(site_pattern_dict, ensure_ascii=False)

if __name__ == '__main__':
    
    if len(sys.argv) != 2:
        print 'Usage: {0} pattern_file'.format(__file__)
        sys.exit(1)

    pattern_file = sys.argv[1]
    trans_pattern_to_json(pattern_file) 
