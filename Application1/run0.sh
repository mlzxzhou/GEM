#!/bin/bash
sdate=20180421
edate=20180430

cdate=$sdate
while [ "$cdate" != "$edate" ];
do
    echo $cdate
    sed "s/DATE/$cdate/g" global_model.py > "global_model_$cdate.py"
    python "global_model_$cdate.py" &>> log0.txt &
    sleep 3h
    cdate=$(date -d "$cdate + 1 day" +%Y%m%d)
done
