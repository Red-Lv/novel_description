#! /bin/bash

for((i = 0; i < 178; i ++))
do
    site_id=${i}
    echo 'site_id: '${site_id}
    python book_name_pen_name_replace.py ${site_id} >./data_3/${site_id}.txt 2>./data_3/${site_id}.txt.wf
done
