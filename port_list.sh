#!/bin/bash

sudo lsof -n -i -P | grep LISTEN | grep -E \
'(nginx|syslog-ng|postgres|supervisor|uwsgi|ipython|rsync|redis|postfix|master|pycharm|phantom|Growl|sshd)' \
| grep '\*:\d*' \
| awk '{printf ("%s\t%s\t%s\t%s\n", $1,$2,$3,$9) }' | sort -k2n -u | column -t | xargs printf "%-10s\t%-6s\t%-10s\t%-8s\n"