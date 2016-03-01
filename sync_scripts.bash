#!/bin/bash

source ~/.bashrc

printf '\n'
for i in mbp2 ub1 ub2 ub4 ub5; do
    if [ $i != $USER ]; then
       printf 'SYNCING %s\n' $i

       #ssh $i "script -qc \"bash -lic 'scr_ed; g-P; git branch -avv | grep ^\* | sed -r \'s/(.*) ([0-9a-f]{7} )(.*)/\2\3/\''\""

       # below works but no output...
       ssh $i "script -qc \"bash -ilc 'scr_ed; g-P'\"; rm typescript;"
       printf '\n\n'
    fi;
done
