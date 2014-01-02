#! /bin/bash

for((i = 0; i < 178; i ++))
do
    site_id=${i}
    #python fetch_description.py ${site_id} 1>./data/${site_id}.txt 2>./data/${site_id}.txt.wf
    echo 'site_id: '.${site_id}
    python LCS.py ./data/${site_id}.txt
done
