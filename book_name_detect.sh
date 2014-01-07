#! /bin/bash

for((i = 0; i < 178; i ++))
do
    site_id=${i}
    echo 'site_id: '${site_id}
    python book_name_pen_name_detect.py ./data_3/${site_id}.txt
done
