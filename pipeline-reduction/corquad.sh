#!/bin/sh
corquad=/data/dupree7/eadams/data/pipeline/corquad/corquad
files=`ls target*.fits`
for file in $files
do
        echo Now correcting ${file}
        ${corquad} ${file}
done
exit 0
