#!/bin/bash

iteration_cnt=${1}

for ((i = 0; i < iteration_cnt; i ++))
do
    sh book_name_pen_name_pattern_detect.sh ./data_${i}/ ./pattern/raw_book_name_pattern.txt.${i}
    sh filter_cs.py ./pattern/raw_book_name_pattern.txt.${i} > ./pattern/raw_book_name_pattern.txt.${i}.filtered
    python pattern_to_json.py ./pattern/raw_book_name_pattern.txt.${i}.filtered > ./pattern/book_name_pattern.json.${i}
    ((next = i + 1))
    mkdir -p ./data_${next}
    sh book_name_pen_name_pattern_replace.sh ./pattern/book_name_pattern.json.${i} ./data_{i} ./data_${next}
done
