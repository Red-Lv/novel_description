#! /bin/bash

data_dir=${1}
pattern_file=${2}

for((i = 0; i < 178; i ++))
do
    site_id=${i}
    echo 'site_id: '${site_id}
    python book_name_pen_name_detect.py ./${data_dir}/${site_id}.txt
done > ${pattern_file}
