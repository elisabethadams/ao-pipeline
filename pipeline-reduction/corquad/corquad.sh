#!/bin/sh
corquad=/home/eadams/src/corquad/corquad
files=`ls [!q]*.fits`
for file in $files
do
        echo Now correcting ${file}
        ${corquad} ${file}
done
exit 0
