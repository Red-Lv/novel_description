#! /bin/bash

book_name_pattern=./pattern/book_name_pattern.json
pen_name_pattern=./pattern/pen_name_pattern.json

data_dir=./data
book_name_replaced_dir=./data_book_name
pen_name_replaced_dir=./data_pen_name

echo 'start replacing book_name'
for((i = 0; i < 178; i ++))
do
    site_id=${i}
    #echo 'site_id: '${site_id}
    python book_name_pattern_replace.py ${book_name_pattern} ${site_id} ${data_dir}/${site_id}.txt 2>./${book_name_replaced_dir}/${site_id}.txt 2>./${book_name_replaced_dir}/${site_id}.txt.wf
done

echo 'start replacing pen_name'
for((i = 0; i < 178; i ++))
do
    site_id=${i}
    #echo 'site_id: '${site_id}
    python pen_name_pattern_replace.py ${pen_name_pattern} ${site_id} ${book_name_replaced_dir}/${site_id}.txt 2>./${pen_name_replaced_dir}/${site_id}.txt 2>./${pen_name_replaced_dir}/${site_id}.txt.wf
done