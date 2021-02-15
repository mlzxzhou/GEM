#!/bin/bash
#sdate=20181112
#edate=20181126
sdate=20181203
edate=20181217

cdate=$sdate
while [ "$cdate" != "$edate" ];
do
    echo $cdate
    sed "s/DATE/$cdate/g" process.py > "global_model_$cdate.py"
    python "global_model_$cdate.py" &>> log0.txt &
    sleep 3h
    cdate=$(date -d "$cdate + 1 day" +%Y%m%d)
done
