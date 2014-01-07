#! /bin/bash

book_name_pattern=${1}
input_data_dir=${2}
output_data_dir=${3}

for((i = 0; i < 178; i ++))
do
    site_id=${i}
    echo 'site_id: '${site_id}
    python book_name_pen_name_pattern_replace.py ${book_name_pattern} ${site_id} ${input_data_dir}/${site_id}.txt.wf >./${output_data_dir}/${site_id}.txt 2>./${output_data_dir}/${site_id}.txt.wf
done
